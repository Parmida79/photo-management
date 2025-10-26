from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from collections import Counter

from app.db import get_db
from app.models import Photo, EmotionAnalysis, ColorAnalysis
from app.utils.helpers import path_id_validator

photo_analysis_router = APIRouter()
emotion_analysis_router = APIRouter()
color_analysis_router = APIRouter()


@photo_analysis_router.get('/{photo_id}')
@path_id_validator
async def get_analysis_status(
    photo_id: str,
    session: Session = Depends(get_db)
):
    """
    Get the analysis status of a photo.
    Useful for tracking Celery task progress.
    """

    photo = session.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    return {
        "photo_id": photo_id,
        "analysis_status": photo.analysis_status,
        "analysis_date": photo.analysis_date,
        "has_caption": bool(photo.caption),
        "has_tags": bool(photo.tags),
        "has_embedding": bool(photo.embedding)
    }

@emotion_analysis_router.get('/')
async def get_emotion_analysis(
        limit: int = Query(50, ge=1, le=200, description="Number of photos to analyze"),
        session: Session = Depends(get_db)
):
    """
    Get comprehensive emotion analysis across all photos.

    This AI-powered feature provides insights into:
    - Overall emotional distribution
    - Most common emotions
    - Emotion confidence patterns
    - Photos with the strongest emotional content
    """

    try:
        # Get emotion analyses
        emotion_analyses = session.query(EmotionAnalysis).limit(limit).all()

        if not emotion_analyses:
            return {
                "total_analyzed": 0,
                "emotion_distribution": {},
                "insights": {},
                "message": "No emotion analysis data available"
            }

        # Analyze emotion distribution
        emotion_counts = Counter()
        confidence_scores = []
        dominant_emotions = []

        for analysis in emotion_analyses:
            dominant_emotions.append(analysis.dominant_emotion)
            confidence_scores.append(analysis.confidence_score)

            if analysis.emotions:
                for emotion, score in analysis.emotions.items():
                    emotion_counts[emotion] += score

        # Calculate insights
        emotion_distribution = dict(emotion_counts.most_common())
        avg_confidence = sum(confidence_scores) / len(confidence_scores)
        most_common_emotion = Counter(dominant_emotions).most_common(1)[0][0]

        return {
            "total_analyzed": len(emotion_analyses),
            "emotion_distribution": emotion_distribution,
            "insights": {
                "most_common_emotion": most_common_emotion,
                "average_confidence": round(avg_confidence, 4),
                "emotion_diversity": len(emotion_distribution),
                "high_confidence_photos": len([c for c in confidence_scores if c > 0.8])
            },
            "top_emotions": list(emotion_distribution.keys())[:5]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emotion analysis failed: {str(e)}")


@color_analysis_router.get('/')
async def get_color_analysis(
        limit: int = Query(50, ge=1, le=200, description="Number of photos to analyze"),
        session: Session = Depends(get_db)
):
    """
    Get comprehensive color analysis across all photos.

    This AI-powered feature provides insights into:
    - Most common colors across photos
    - Brightness and saturation patterns
    - Color palette trends
    - Visual style preferences
    """

    try:
        # Get color analyses
        color_analyses = session.query(ColorAnalysis).limit(limit).all()

        if not color_analyses:
            return {
                "total_analyzed": 0,
                "color_insights": {},
                "message": "No color analysis data available"
            }

        # Analyze color patterns
        color_counts = Counter()
        brightness_scores = []
        saturation_scores = []

        for analysis in color_analyses:
            brightness_scores.append(analysis.brightness)
            saturation_scores.append(analysis.saturation)

            if analysis.dominant_colors:
                for color_info in analysis.dominant_colors:
                    color_counts[color_info.get('hex', '')] += color_info.get('percentage', 0)

        # Calculate insights
        avg_brightness = sum(brightness_scores) / len(brightness_scores)
        avg_saturation = sum(saturation_scores) / len(saturation_scores)
        most_common_colors = color_counts.most_common(10)

        return {
            "total_analyzed": len(color_analyses),
            "color_insights": {
                "most_common_colors": [{"hex": color, "frequency": freq} for color, freq in most_common_colors],
                "average_brightness": round(avg_brightness, 4),
                "average_saturation": round(avg_saturation, 4),
                "brightness_range": {
                    "min": round(min(brightness_scores), 4),
                    "max": round(max(brightness_scores), 4)
                },
                "saturation_range": {
                    "min": round(min(saturation_scores), 4),
                    "max": round(max(saturation_scores), 4)
                }
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Color analysis failed: {str(e)}")

