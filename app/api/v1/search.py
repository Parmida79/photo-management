from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
import json

from app.db import get_db
from app.models import Photo
from app.services.ai_service import ai_service

semantic_search_router = APIRouter()

@semantic_search_router.get('/')
async def semantic_search(
    q: str = Query(..., description="Search query for semantic similarity"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    threshold: float = Query(0.7, ge=0.0, le=1.0, description="Minimum similarity threshold"),
    session: Session = Depends(get_db)
):
    """
    Perform semantic search on photos using AI-generated embeddings.
    
    This endpoint:
    1. Generates an embedding for the search query using AI
    2. Compares it with stored photo embeddings using cosine similarity
    3. Returns photos ranked by semantic similarity
    4. Includes similarity scores and metadata
    
    The search is based on the AI-generated captions and tags of photos,
    allowing users to find photos by meaning rather than exact text matches.
    """
    
    if not q.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    try:
        # Generate embedding for search query
        query_embedding = await ai_service._generate_embedding(q)
        
        # Get all photos with completed analysis
        photos = session.query(Photo).filter(
            Photo.analysis_status == "completed",
            Photo.embedding.isnot(None)
        ).all()
        
        if not photos:
            return {
                "query": q,
                "results": [],
                "total_found": 0,
                "message": "No analyzed photos found"
            }
        
        # Calculate similarities
        similarities = []
        for photo in photos:
            if photo.embedding:
                try:
                    # Parse embedding if it's stored as JSON string
                    if isinstance(photo.embedding, str):
                        embedding = json.loads(photo.embedding)
                    else:
                        embedding = photo.embedding
                    
                    similarity = ai_service.calculate_similarity(query_embedding, embedding)
                    
                    if similarity >= threshold:
                        similarities.append({
                            "photo": photo,
                            "similarity": similarity
                        })
                except Exception as e:
                    print(f"Error calculating similarity for photo {photo.id}: {e}")
                    continue
        
        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Limit results
        similarities = similarities[:limit]
        
        # Format results
        results = []
        for item in similarities:
            photo = item["photo"]
            similarity = item["similarity"]
            
            results.append({
                "id": photo.id,
                "filename": photo.filename,
                "original_filename": photo.original_filename,
                "upload_date": photo.created_at,
                "caption": photo.caption,
                "tags": photo.tags,
                "similarity_score": round(similarity, 4),
                "width": photo.width,
                "height": photo.height
            })
        
        return {
            "query": q,
            "results": results,
            "total_found": len(results),
            "threshold": threshold,
            "search_type": "semantic_similarity"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@semantic_search_router.get('/tags')
async def search_by_tags(
    tags: str = Query(..., description="Comma-separated list of tags to search for"),
    match_all: bool = Query(False, description="Whether to match all tags (AND) or any tags (OR)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    session: Session = Depends(get_db)
):
    """
    Search photos by tags using exact matching.
    
    This provides traditional tag-based search as a complement to semantic search.
    """
    
    if not tags.strip():
        raise HTTPException(status_code=400, detail="Tags cannot be empty")
    
    try:
        # Parse tags
        search_tags = [tag.strip().lower() for tag in tags.split(",") if tag.strip()]
        
        if not search_tags:
            raise HTTPException(status_code=400, detail="No valid tags provided")
        
        # Get photos with completed analysis
        photos_query = session.query(Photo).filter(Photo.analysis_status == "completed")
        
        if match_all:
            # Match all tags (AND logic)
            for tag in search_tags:
                photos_query = photos_query.filter(Photo.tags.contains([tag]))
        else:
            # Match any tag (OR logic)
            from sqlalchemy import or_
            tag_conditions = [Photo.tags.contains([tag]) for tag in search_tags]
            photos_query = photos_query.filter(or_(*tag_conditions))
        
        photos = photos_query.limit(limit).all()
        
        # Format results
        results = []
        for photo in photos:
            # Calculate tag match score
            photo_tags = [tag.lower() for tag in (photo.tags or [])]
            matched_tags = [tag for tag in search_tags if tag in photo_tags]
            match_score = len(matched_tags) / len(search_tags) if search_tags else 0
            
            results.append({
                "id": photo.id,
                "filename": photo.filename,
                "original_filename": photo.original_filename,
                "upload_date": photo.created_at,
                "caption": photo.caption,
                "tags": photo.tags,
                "matched_tags": matched_tags,
                "match_score": round(match_score, 4),
                "width": photo.width,
                "height": photo.height
            })
        
        # Sort by match score
        results.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "query_tags": search_tags,
            "match_all": match_all,
            "results": results,
            "total_found": len(results),
            "search_type": "tag_matching"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tag search failed: {str(e)}")

@semantic_search_router.get('/emotions')
async def search_by_emotions(
    emotion: str = Query(..., description="Emotion to search for (happy, sad, excited, calm, surprised, etc.)"),
    min_confidence: float = Query(0.5, ge=0.0, le=1.0, description="Minimum confidence threshold"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    session: Session = Depends(get_db)
):
    """
    Search photos by dominant emotion using AI emotion analysis.
    
    This is an AI-powered smart feature that allows users to find photos
    based on the emotional content detected by AI analysis.
    """
    
    if not emotion.strip():
        raise HTTPException(status_code=400, detail="Emotion cannot be empty")
    
    try:
        # Search for photos with the specified emotion
        from app.models import EmotionAnalysis

        emotion_analyses = session.query(EmotionAnalysis).filter(
            EmotionAnalysis.dominant_emotion.ilike(f"%{emotion.lower()}%"),
            EmotionAnalysis.confidence_score >= min_confidence
        ).limit(limit).all()
        
        # Get photo details
        results = []
        for analysis in emotion_analyses:
            photo = session.query(Photo).filter(Photo.id == analysis.photo_id).first()
            if photo:
                results.append({
                    "id": photo.id,
                    "filename": photo.filename,
                    "original_filename": photo.original_filename,
                    "upload_date": photo.created_at,
                    "caption": photo.caption,
                    "tags": photo.tags,
                    "dominant_emotion": analysis.dominant_emotion,
                    "emotion_confidence": round(analysis.confidence_score, 4),
                    "all_emotions": analysis.emotions,
                    "width": photo.width,
                    "height": photo.height
                })
        
        # Sort by confidence score
        results.sort(key=lambda x: x["emotion_confidence"], reverse=True)
        
        return {
            "query_emotion": emotion,
            "min_confidence": min_confidence,
            "results": results,
            "total_found": len(results),
            "search_type": "emotion_analysis"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emotion search failed: {str(e)}")

@semantic_search_router.get('/colors')
async def search_by_colors(
    color: str = Query(..., description="Color to search for (hex code or color name)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    session: Session = Depends(get_db)
):
    """
    Search photos by dominant colors using AI color analysis.
    
    This is an AI-powered smart feature that allows users to find photos
    based on their dominant colors detected by AI analysis.
    """
    
    if not color.strip():
        raise HTTPException(status_code=400, detail="Color cannot be empty")
    
    try:
        # Normalize color input
        color_query = color.strip().lower()
        
        # Search for photos with the specified color
        from app.models import ColorAnalysis

        color_analyses = session.query(ColorAnalysis).all()
        
        results = []
        for analysis in color_analyses:
            if analysis.dominant_colors:
                # Check if any dominant color matches the query
                for color_info in analysis.dominant_colors:
                    hex_color = color_info.get('hex', '').lower()
                    if color_query in hex_color or color_query in color_info.get('rgb', []):
                        photo = session.query(Photo).filter(Photo.id == analysis.photo_id).first()
                        if photo:
                            results.append({
                                "id": photo.id,
                                "filename": photo.filename,
                                "original_filename": photo.original_filename,
                                "upload_date": photo.created_at,
                                "caption": photo.caption,
                                "tags": photo.tags,
                                "matched_color": color_info,
                                "dominant_colors": analysis.dominant_colors,
                                "brightness": analysis.brightness,
                                "saturation": analysis.saturation,
                                "width": photo.width,
                                "height": photo.height
                            })
                            break
        
        # Limit results
        results = results[:limit]
        
        return {
            "query_color": color,
            "results": results,
            "total_found": len(results),
            "search_type": "color_analysis"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Color search failed: {str(e)}")
