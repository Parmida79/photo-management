import json

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Photo, Album
from app.services.ai_service import ai_service
from app.utils.helpers import _generate_album_info

album_generator_router = APIRouter()

@album_generator_router.post('/')
async def generate_ai_album(
        theme: str = Query(..., description="Theme for the AI-generated album"),
        max_photos: int = Query(20, ge=1, le=100, description="Maximum number of photos in album"),
        session: Session = Depends(get_db)
):
    """
    Generate an AI-powered album based on a theme.

    This is a mandatory AI-powered smart feature that:
    1. Uses AI to analyze photo content and group them by theme
    2. Generates intelligent album names and descriptions
    3. Uses semantic similarity to find photos matching the theme
    4. Creates a curated collection of photos

    The AI analyzes photo captions, tags, emotions, and colors to create
    meaningful groupings that go beyond simple tag matching.
    """

    if not theme.strip():
        raise HTTPException(status_code=400, detail="Theme cannot be empty")

    try:
        # Generate embedding for the theme
        theme_embedding = await ai_service._generate_embedding(theme)

        # Get all photos with completed analysis
        photos = session.query(Photo).filter(
            Photo.analysis_status == "completed",
            Photo.embedding.isnot(None)
        ).all()

        if not photos:
            raise HTTPException(status_code=404, detail="No analyzed photos found")

        # Calculate theme similarity for each photo
        photo_scores = []
        for photo in photos:
            if photo.embedding:
                try:
                    if isinstance(photo.embedding, str):
                        embedding = json.loads(photo.embedding)
                    else:
                        embedding = photo.embedding

                    similarity = ai_service.calculate_similarity(theme_embedding, embedding)

                    # Boost score based on tags and caption relevance
                    tag_boost = 0
                    if photo.tags:
                        theme_words = theme.lower().split()
                        for tag in photo.tags:
                            if any(word in tag.lower() for word in theme_words):
                                tag_boost += 0.1

                    final_score = similarity + tag_boost
                    photo_scores.append({
                        "photo": photo,
                        "score": final_score
                    })
                except Exception as e:
                    print(f"Error calculating theme similarity for photo {photo.id}: {e}")
                    continue

        # Sort by relevance score
        photo_scores.sort(key=lambda x: x["score"], reverse=True)

        # Select top photos for the album
        selected_photos = photo_scores[:max_photos]

        if not selected_photos:
            raise HTTPException(status_code=404, detail="No photos match the theme")

        # Generate AI-powered album name and description
        album_info = await _generate_album_info(theme, selected_photos)

        # Create album record
        album = Album(
            name=album_info["name"],
            description=album_info["description"],
            is_ai_generated=True,
            theme=theme,
            photo_ids=[item["photo"].id for item in selected_photos]
        )

        session.add(album)
        session.commit()
        session.refresh(album)

        # Format response
        album_photos = []
        for item in selected_photos:
            photo = item["photo"]
            album_photos.append({
                "id": photo.id,
                "filename": photo.filename,
                "original_filename": photo.original_filename,
                "caption": photo.caption,
                "tags": photo.tags,
                "relevance_score": round(item["score"], 4),
                "upload_date": photo.upload_date
            })

        return {
            "album_id": album.id,
            "name": album.name,
            "description": album.description,
            "theme": theme,
            "is_ai_generated": True,
            "photo_count": len(album_photos),
            "photos": album_photos,
            "created_date": album.created_at
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Album generation failed: {str(e)}")
