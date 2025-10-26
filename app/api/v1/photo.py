from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request, Query
from fastapi_filter import FilterDepends
from fastapi_pagination.links import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
import os
import uuid
import aiofiles
from PIL import Image

from app.config import settings
from app.db import get_db
from app.filters import UploadPhotoFilter
from app.models import Photo
from app.schemas import UploadPhotoResponse, UploadPhotosResponse
from app.utils.helpers import path_id_validator

upload_photo_router = APIRouter()

class PhotoResponse:
    def __init__(self, photo: Photo):
        self.id = photo.id
        self.filename = photo.filename
        self.original_filename = photo.original_filename
        self.file_size = photo.file_size
        self.mime_type = photo.mime_type
        self.upload_date = photo.created_at
        self.width = photo.width
        self.height = photo.height
        self.caption = photo.caption
        self.tags = photo.tags
        self.analysis_status = photo.analysis_status
        self.analysis_date = photo.analysis_date


@upload_photo_router.post('/')
async def upload_photo(
    request: Request,
    file: UploadFile = File(...),
    session: Session = Depends(get_db),
):
    """
    Upload a photo and trigger AI analysis.
    
    This endpoint:
    1. Validates the uploaded file
    2. Stores the file on disk
    3. Saves photo metadata to database
    4. Triggers async AI analysis
    5. Returns photo ID for future reference
    """
    
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed types: {settings.allowed_extensions}"
        )
    
    # Check file size
    file_content = await file.read()
    if len(file_content) > settings.max_file_size:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size: {settings.max_file_size} bytes"
        )
    
    try:
        # Generate unique filename
        photo_id = str(uuid.uuid4())
        filename = f"{photo_id}{file_ext}"
        file_path = os.path.join(settings.upload_dir, filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Get image dimensions
        try:
            with Image.open(file_path) as img:
                width, height = img.size
        except Exception:
            width, height = None, None
        
        # Create database record
        photo = Photo(
            id=photo_id,
            filename=filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=len(file_content),
            mime_type=file.content_type or "image/jpeg",
            width=width,
            height=height,
            analysis_status="pending"
        )
        
        session.add(photo)
        session.commit()
        session.refresh(photo)

        return {
            "message": "Photo uploaded successfully",
            "photo_id": photo_id,
            "filename": filename,
            "status": "pending_analysis"
        }
        
    except Exception as e:
        # Clean up file if database operation fails
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@upload_photo_router.get('/{photo_id}', response_model=UploadPhotoResponse)
@path_id_validator
async def get_photo(
    photo_id: str,
    session: Session = Depends(get_db)
):
    """
    Retrieve photo metadata including AI-generated analysis.

    Returns:
    - Basic photo information (filename, upload date, dimensions)
    - AI-generated tags (at least 5 relevant tags)
    - AI-generated caption (short descriptive sentence)
    - Analysis status and date
    """

    photo = session.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    return photo

@upload_photo_router.get('/', response_model=Page[UploadPhotosResponse])
async def list_photos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    param: UploadPhotoFilter = FilterDepends(UploadPhotoFilter),
    session: Session = Depends(get_db)
):
    """
    List all photos with pagination.
    """

    photos = session.query(Photo).offset(skip).limit(limit)

    photos = param.filter(photos)
    photos = param.sort(photos)

    return paginate(photos)

@upload_photo_router.delete('/{photo_id}')
@path_id_validator
async def delete_photo(
    photo_id: str,
    session: Session = Depends(get_db)
):
    """
    Delete a photo and its associated files.
    """

    photo = session.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    try:
        # Delete file from disk
        if os.path.exists(photo.file_path):
            os.remove(photo.file_path)

        # Delete from database
        session.delete(photo)
        session.commit()

        return {"message": "Photo deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

