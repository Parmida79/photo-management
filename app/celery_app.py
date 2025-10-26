from celery import Celery
import asyncio
import os

from app import settings
from app.db import SessionLocal
from app.models import Photo, EmotionAnalysis, ColorAnalysis, DailySummary
from app.services.ai_service import ai_service

# Create Celery app
celery_app = Celery(
    "photo_management",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['app.tasks.photo_analysis']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)


@celery_app.task(bind=True)
def analyze_photo_task(self, photo_id: str, file_path: str):
    """
    Celery task for async photo analysis.

    This task runs AI analysis on uploaded photos in the background,
    allowing the API to respond quickly while processing continues.
    """
    from datetime import datetime

    db = SessionLocal()
    try:
        # Update task status
        self.update_state(state='PROGRESS', meta={'status': 'Starting analysis'})

        # Get photo from database
        photo = db.query(Photo).filter(Photo.id == photo_id).first()
        if not photo:
            return {'status': 'error', 'message': 'Photo not found'}

        # Update photo status to processing
        photo.analysis_status = "processing"
        db.commit()

        # Update task status
        self.update_state(state='PROGRESS', meta={'status': 'Running AI analysis'})

        # Run AI analysis (this is async, so we need to run it in event loop)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            analysis_results = loop.run_until_complete(
                ai_service.analyze_image(file_path)
            )
        finally:
            loop.close()

        # Update task status
        self.update_state(state='PROGRESS', meta={'status': 'Saving results'})

        # Update photo with analysis results
        photo.caption = analysis_results.get('caption', '')
        photo.tags = analysis_results.get('tags', [])
        photo.embedding = analysis_results.get('embedding', [])
        photo.analysis_status = "completed"
        photo.analysis_date = datetime.utcnow()

        db.commit()

        # Store emotion analysis
        if 'emotions' in analysis_results:
            emotion_analysis = EmotionAnalysis(
                photo_id=photo_id,
                emotions=analysis_results['emotions'].get('emotions', {}),
                dominant_emotion=analysis_results['emotions'].get('dominant_emotion', 'neutral'),
                confidence_score=analysis_results['emotions'].get('confidence', 0.5)
            )
            db.add(emotion_analysis)

        # Store color analysis
        if 'colors' in analysis_results:
            color_analysis = ColorAnalysis(
                photo_id=photo_id,
                dominant_colors=analysis_results['colors'].get('dominant_colors', []),
                color_palette=analysis_results['colors'].get('color_palette', []),
                brightness=analysis_results['colors'].get('brightness', 0.5),
                saturation=analysis_results['colors'].get('saturation', 0.3)
            )
            db.add(color_analysis)

        db.commit()

        return {
            'status': 'completed',
            'photo_id': photo_id,
            'caption': photo.caption,
            'tags': photo.tags,
            'analysis_date': photo.analysis_date.isoformat()
        }

    except Exception as e:
        # Update photo status to failed
        photo = db.query(Photo).filter(Photo.id == photo_id).first()
        if photo:
            photo.analysis_status = "failed"
            db.commit()

        return {
            'status': 'error',
            'message': str(e),
            'photo_id': photo_id
        }

    finally:
        db.close()


@celery_app.task
def cleanup_old_analyses():
    """
    Periodic task to clean up old analysis data and optimize database.
    """
    from datetime import datetime, timedelta

    db = SessionLocal()
    try:
        # Clean up photos with failed analysis older than 7 days
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        old_failed_photos = db.query(Photo).filter(
            Photo.analysis_status == "failed",
            Photo.created_at < cutoff_date
        ).all()

        for photo in old_failed_photos:
            # Delete file if it exists
            if os.path.exists(photo.file_path):
                os.remove(photo.file_path)

            # Delete from database
            db.delete(photo)

        db.commit()

        return {
            'status': 'completed',
            'cleaned_photos': len(old_failed_photos)
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

    finally:
        db.close()


@celery_app.task
def generate_daily_summaries():
    """
    Periodic task to generate daily summaries for recent days.
    """
    from datetime import datetime, timedelta

    db = SessionLocal()
    try:
        # Generate summaries for the last 7 days
        summaries_created = 0

        for days_ago in range(1, 8):
            target_date = datetime.utcnow() - timedelta(days=days_ago)
            date_str = target_date.date().isoformat()

            # Check if summary already exists
            existing_summary = db.query(DailySummary).filter(
                DailySummary.date == datetime.combine(target_date.date(), datetime.min.time())
            ).first()

            if not existing_summary:
                # Get photos for this date
                photos = db.query(Photo).filter(
                    Photo.analysis_status == "completed",
                    Photo.created_at >= datetime.combine(target_date.date(), datetime.min.time()),
                    Photo.created_at < datetime.combine(target_date.date(), datetime.min.time()).replace(
                        day=target_date.day + 1)
                ).all()

                if photos:
                    # Create basic summary (AI generation would be called separately)
                    daily_summary = DailySummary(
                        date=datetime.combine(target_date.date(), datetime.min.time()),
                        photo_count=len(photos),
                        summary_text=f"Day with {len(photos)} photos"
                    )
                    db.add(daily_summary)
                    summaries_created += 1

        db.commit()

        return {
            'status': 'completed',
            'summaries_created': summaries_created
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

    finally:
        db.close()


# Celery beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    'cleanup-old-analyses': {
        'task': 'app.celery_app.cleanup_old_analyses',
        'schedule': 86400.0,  # Run daily
    },
    'generate-daily-summaries': {
        'task': 'app.celery_app.generate_daily_summaries',
        'schedule': 3600.0,  # Run hourly
    },
}

