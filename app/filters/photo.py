from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter

from app.models import Photo


class UploadPhotoFilter(Filter):
    id: Optional[int]
    order_by: Optional[List[str]]
    # search: Optional[str]

    class Constants(Filter.Constants):
        model = Photo

