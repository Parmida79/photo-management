from datetime import datetime
from typing import Optional, List

from app.schemas.base_serializer import BaseSerializer


class UploadPhotoResponse(BaseSerializer):
    id: str
    created_at: datetime
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    upload_date: str
    width: int
    height: int
    caption: Optional[str] = None
    tags: Optional[List[str]] = []
    analysis_status: str
    analysis_date: Optional[datetime] = None



class UploadPhotosResponse(BaseSerializer):
    id: str
    created_at: datetime
    filename: str
    original_filename: str
    analysis_status: str
    caption: Optional[str] = None
    tags: Optional[List[str]] = []


# class PhotoStatusResponse(BaseSerializer):
#     id: str
#     created_at: datetime
#     analysis_status: str
#     analysis_date: Optional[datetime] = None
#     has_caption: bool
#     has_tags: bool
#     has_embeddings: bool

