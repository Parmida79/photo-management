from functools import wraps

from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
import json
from collections import Counter

from app.models import Photo, EmotionAnalysis
from app.services.ai_service import ai_service


def path_id_validator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        path_parameters = kwargs['request'].path_params
        query_parameters = dict(kwargs['request'].query_params)
        path_parameters.update(query_parameters)

        if path_parameters is not None:
            for i in path_parameters:
                if i.endswith('id'):
                    try:
                        path_id = int(path_parameters[i])
                        if path_id <= 0:
                            # TODO: add i to message
                            raise HTTPException(status_code=404, detail='Id Not Found')

                    except (ValueError, TypeError):
                        i = i.replace('_', ' ').strip().title()
                        raise HTTPException(status_code=404, detail='Invalid ' + i + ' Given In Path')

        if query_parameters is not None:
            for i in query_parameters:
                if i is not None and (i.endswith('Id') or i.endswith('_id')):
                    try:
                        path_id = int(path_parameters[i])
                        if path_id <= 0:
                            # TODO: add i to message
                            raise HTTPException(status_code=404, detail='Id Not Found')

                    except (ValueError, TypeError):
                        i = i.replace('_', ' ').strip().title()
                        raise HTTPException(status_code=404, detail='Invalid ' + i + ' Given In Path')

        return func(*args, **kwargs)

    return wrapper


def convert_to_camel(word):
    i_s = word.split('_')
    output = ''

    if len(i_s) > 1:
        for i in range(len(i_s)):
            if i == 0:
                output = ''.join(i_s[0])
            else:
                i_s[i] = i_s[i].title()
                output = ''.join(i_s)
                i += 1
    else:
        output = ''.join(word)

    return output


# Helper functions for AI-powered features
async def _generate_album_info(theme: str, selected_photos: List[Dict]) -> Dict:
    """Generate AI-powered album name and description."""
    try:
        if not ai_service.client:
            return {
                "name": f"{theme.title()} Collection",
                "description": f"A curated collection of {len(selected_photos)} photos themed around {theme}."
            }

        # Create context from selected photos
        photo_context = []
        for item in selected_photos[:5]:  # Use top 5 photos for context
            photo = item["photo"]
            photo_context.append(f"Photo: {photo.caption or 'No caption'}, Tags: {', '.join(photo.tags or [])}")

        context = "\n".join(photo_context)

        response = ai_service.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a creative photo curator. Generate engaging album names and descriptions based on photo themes and content."
                },
                {
                    "role": "user",
                    "content": f"""Create an album name and description for a photo collection with theme "{theme}".

                Photos in the collection:
                {context}

                Generate:
                1. A creative, engaging album name (max 50 characters)
                2. A descriptive summary (max 200 characters)

                Format as JSON:
                {{
                    "name": "album name",
                    "description": "album description"
                }}"""
                }
            ],
            max_tokens=200,
            temperature=0.7
        )

        content = response.choices[0].message.content
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        json_str = content[json_start:json_end]

        return json.loads(json_str)

    except Exception as e:
        print(f"Error generating album info: {e}")

        return {
            "name": f"{theme.title()} Collection",
            "description": f"A curated collection of {len(selected_photos)} photos themed around {theme}."
        }


async def _generate_daily_summary_ai(
        date_str: str,
        photos: List[Photo],
        emotions_data: List[Dict],
        colors_data: List[Dict],
        themes_data: List[str]
) -> Dict:
    """Generate AI-powered daily summary."""
    try:
        if not ai_service.client:
            return _generate_fallback_summary(photos, emotions_data, colors_data, themes_data)

        # Prepare data for AI analysis
        emotion_summary = Counter([e["dominant"] for e in emotions_data])
        color_summary = []
        for colors in colors_data:
            if colors["dominant_colors"]:
                color_summary.extend([c["hex"] for c in colors["dominant_colors"][:3]])

        theme_summary = Counter(themes_data)

        response = ai_service.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a photo diary analyst. Create engaging daily summaries of photo collections."
                },
                {
                    "role": "user",
                    "content": f"""Create a daily photo summary for {date_str}:

                Photos: {len(photos)}
                Dominant emotions: {dict(emotion_summary.most_common(3))}
                Common colors: {Counter(color_summary).most_common(5)}
                Popular themes: {dict(theme_summary.most_common(5))}

                Generate a JSON response with:
                {{
                    "summary_text": "engaging 2-3 sentence summary",
                    "mood": "overall mood description",
                    "visual_style": "description of visual style",
                    "dominant_emotions": {dict(emotion_summary.most_common(3))},
                    "dominant_colors": {Counter(color_summary).most_common(5)},
                    "themes": {dict(theme_summary.most_common(5))}
                }}"""
                }
            ],
            max_tokens=300,
            temperature=0.6
        )

        content = response.choices[0].message.content
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        json_str = content[json_start:json_end]

        return json.loads(json_str)

    except Exception as e:
        print(f"Error generating daily summary: {e}")
        return _generate_fallback_summary(photos, emotions_data, colors_data, themes_data)


def _generate_fallback_summary(photos: List[Photo], emotions_data: List[Dict], colors_data: List[Dict],
                               themes_data: List[str]) -> Dict:
    """Generate fallback summary when AI is unavailable."""
    emotion_summary = Counter([e["dominant"] for e in emotions_data])
    color_summary = []
    for colors in colors_data:
        if colors["dominant_colors"]:
            color_summary.extend([c["hex"] for c in colors["dominant_colors"][:3]])

    theme_summary = Counter(themes_data)

    return {
        "summary_text":
            f"A day with {len(photos)} photos, featuring "
            f"{emotion_summary.most_common(1)[0][0] if emotion_summary else 'various'} "
            f"emotions and {len(set(color_summary))} different color tones.",
        "mood": emotion_summary.most_common(1)[0][0] if emotion_summary else "neutral",
        "visual_style": "diverse visual content",
        "dominant_emotions": dict(emotion_summary.most_common(3)),
        "dominant_colors": Counter(color_summary).most_common(5),
        "themes": dict(theme_summary.most_common(5))
    }


async def _analyze_photo_trends(photos: List[Photo], session: Session) -> Dict:
    """Analyze photo trends over time."""
    try:
        # Group photos by date
        photos_by_date = {}
        for photo in photos:
            date_key = photo.created_at.date().isoformat()
            if date_key not in photos_by_date:
                photos_by_date[date_key] = []
            photos_by_date[date_key].append(photo)

        # Analyze trends
        upload_trends = {date: len(photo_list) for date, photo_list in photos_by_date.items()}

        # Get emotion trends
        emotion_trends = {}
        for date, photo_list in photos_by_date.items():
            emotions = []
            for photo in photo_list:
                emotion_analysis = session.query(EmotionAnalysis).filter(
                    EmotionAnalysis.photo_id == photo.id
                ).first()
                if emotion_analysis:
                    emotions.append(emotion_analysis.dominant_emotion)

            if emotions:
                emotion_trends[date] = Counter(emotions).most_common(3)

        return {
            "upload_patterns": upload_trends,
            "emotion_trends": emotion_trends,
            "total_days": len(photos_by_date),
            "average_photos_per_day": round(len(photos) / len(photos_by_date), 2) if photos_by_date else 0
        }

    except Exception as e:
        print(f"Error analyzing trends: {e}")
        return {"error": "Trend analysis failed"}

