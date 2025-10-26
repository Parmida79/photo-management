from fastapi import APIRouter

from app.api.v1.album import album_generator_router
from app.api.v1.analysis import photo_analysis_router, emotion_analysis_router, color_analysis_router
from app.api.v1.photo import upload_photo_router, photo_router
from app.api.v1.search import semantic_search_router
from app.api.v1.statistics import daily_summary_router, trend_router

# if restricted APIs are needed (access with token)
# oauth2_scheme = APIKeyHeader(name='Authorization')
# restricted_router = APIRouter(prefix='/restricted/photo-management/api/v1', dependencies=[Depends(oauth2_scheme)])

public_router = APIRouter(prefix='/public/photo-management/api/v1')


# Photo
public_router.include_router(
    upload_photo_router,
    prefix='/upload',
    tags=['upload'],
)
public_router.include_router(
    photo_router,
    prefix='/photos',
    tags=['upload'],
)

# Search
public_router.include_router(
    semantic_search_router,
    prefix='/search',
    tags=['semantic-search'],
)

# Analysis
public_router.include_router(
    photo_analysis_router,
    prefix='/photo-analysis',
    tags=['photo-status-analysis'],
)
public_router.include_router(
    emotion_analysis_router,
    prefix='/emotion-analysis',
    tags=['emotion-analysis'],
)
public_router.include_router(
    color_analysis_router,
    prefix='/color-analysis',
    tags=['color-analysis'],
)

# Statistics
public_router.include_router(
    daily_summary_router,
    prefix='/daily-summary',
    tags=['daily-summary'],
)
public_router.include_router(
    trend_router,
    prefix='/trends',
    tags=['trends'],
)


# Album
public_router.include_router(
    album_generator_router,
    prefix='/albums-generator',
    tags=['albums-generator'],
)

