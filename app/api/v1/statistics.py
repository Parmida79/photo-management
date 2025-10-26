from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Photo, EmotionAnalysis, ColorAnalysis, DailySummary
from app.utils.helpers import _generate_daily_summary_ai, _analyze_photo_trends

daily_summary_router = APIRouter()
trend_router = APIRouter()

@daily_summary_router.get('/{date_str}')
async def get_daily_summary(
        date_str: str,
        session: Session = Depends(get_db)
):
    """
    Generate AI-powered daily summary of photos.

    This is a mandatory AI-powered smart feature that:
    1. Analyzes all photos uploaded on a specific date
    2. Uses AI to generate insights about the day's photos
    3. Identifies dominant emotions, colors, and themes
    4. Creates a narrative summary of the day's visual story

    The AI combines emotion analysis, color analysis, and semantic understanding
    to create meaningful daily summaries.
    """

    try:
        # Parse date
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        # Get photos from the specified date
        photos = session.query(Photo).filter(
            Photo.analysis_status == "completed",
            Photo.created_at >= datetime.combine(target_date, datetime.min.time()),
            Photo.created_at < datetime.combine(target_date, datetime.min.time()).replace(day=target_date.day + 1)
        ).all()

        if not photos:
            return {
                "date": date_str,
                "photo_count": 0,
                "summary": "No photos found for this date",
                "insights": {}
            }

        # Analyze emotions
        emotions_data = []
        colors_data = []
        themes_data = []

        for photo in photos:
            # Get emotion analysis
            emotion_analysis = session.query(EmotionAnalysis).filter(
                EmotionAnalysis.photo_id == photo.id
            ).first()

            if emotion_analysis:
                emotions_data.append({
                    "dominant": emotion_analysis.dominant_emotion,
                    "confidence": emotion_analysis.confidence_score,
                    "all_emotions": emotion_analysis.emotions
                })

            # Get color analysis
            color_analysis = session.query(ColorAnalysis).filter(
                ColorAnalysis.photo_id == photo.id
            ).first()

            if color_analysis:
                colors_data.append({
                    "dominant_colors": color_analysis.dominant_colors,
                    "brightness": color_analysis.brightness,
                    "saturation": color_analysis.saturation
                })

            # Collect themes from tags and captions
            if photo.tags:
                themes_data.extend(photo.tags)
            if photo.caption:
                themes_data.append(photo.caption)

        # Generate AI summary
        summary_data = await _generate_daily_summary_ai(
            date_str, photos, emotions_data, colors_data, themes_data
        )

        # Create or update daily summary record
        existing_summary = session.query(DailySummary).filter(
            DailySummary.date == datetime.combine(target_date, datetime.min.time())
        ).first()

        if existing_summary:
            existing_summary.photo_count = len(photos)
            existing_summary.dominant_emotions = summary_data["dominant_emotions"]
            existing_summary.dominant_colors = summary_data["dominant_colors"]
            existing_summary.themes = summary_data["themes"]
            existing_summary.summary_text = summary_data["summary_text"]
            session.commit()
            summary_id = existing_summary.id
        else:
            daily_summary = DailySummary(
                date=datetime.combine(target_date, datetime.min.time()),
                photo_count=len(photos),
                dominant_emotions=summary_data["dominant_emotions"],
                dominant_colors=summary_data["dominant_colors"],
                themes=summary_data["themes"],
                summary_text=summary_data["summary_text"]
            )
            session.add(daily_summary)
            session.commit()
            session.refresh(daily_summary)
            summary_id = daily_summary.id

        return {
            "date": date_str,
            "photo_count": len(photos),
            "summary": summary_data["summary_text"],
            "insights": {
                "dominant_emotions": summary_data["dominant_emotions"],
                "dominant_colors": summary_data["dominant_colors"],
                "themes": summary_data["themes"],
                "mood": summary_data["mood"],
                "visual_style": summary_data["visual_style"]
            },
            "photos": [
                {
                    "id": photo.id,
                    "filename": photo.filename,
                    "caption": photo.caption,
                    "tags": photo.tags,
                    "upload_time": photo.created_at
                }
                for photo in photos
            ]
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Daily summary generation failed: {str(e)}")


@trend_router.get('/')
async def get_photo_trends(
        days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
        session: Session = Depends(get_db)
):
    """
    Analyze photo trends over time using AI insights.

    This AI-powered feature analyzes patterns in:
    - Emotion trends over time
    - Color preferences
    - Popular themes and subjects
    - Upload patterns and habits
    """

    try:
        from datetime import timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get photos from the specified period
        photos = session.query(Photo).filter(
            Photo.analysis_status == "completed",
            Photo.created_at >= start_date,
            Photo.created_at <= end_date
        ).all()

        if not photos:
            return {
                "period_days": days,
                "total_photos": 0,
                "trends": {},
                "message": "No photos found in the specified period"
            }

        # Analyze trends
        trends = await _analyze_photo_trends(photos, session)

        return {
            "period_days": days,
            "total_photos": len(photos),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "trends": trends
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")

