import io
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1 import public_router
from app.db import Base, engine, create_database_if_not_exists

# Import all models to ensure they're registered with Base.metadata
from app.models import Photo  # noqa: F401

# Set environment variables for Hugging Face
os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/photo_management")
os.environ.setdefault("UPLOAD_DIR", "./uploads")


# Create database and tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # First ensure the database exists
    try:
        create_database_if_not_exists()
        # Then create all tables
        Base.metadata.create_all(bind=engine)
        print("Database initialization completed successfully")
    except Exception as e:
        print(f"Error during database initialization: {e}")
        raise
    yield
    # Shutdown
    pass


def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("VERSION")
    """
    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


app = FastAPI(
    title="AI-Powered Photo Management Service",
    description="A cloud-based photo management service with AI-powered analysis and semantic search",
    version=read('VERSION'),
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_url='/openapi.json',
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # expose_headers=["*"]
)

# Include routers
app.include_router(public_router)
# app.include_router(restricted_router)

@app.get("/")
async def root():
    return {
        "message": "AI-Powered Photo Management Service",
        "version": "1.0.0",
        "endpoints": {
            "upload": "POST /api/v1/upload",
            "get_photo": "GET /api/v1/photos/{photo_id}",
            "list_photos": "GET /api/v1/photos",
            "delete_photo": "GET /api/v1/photos",
            "search": "GET /api/v1/search?q={query}",
            "tag": "GET /api/v1/search/tags?q={query}",
            "emotion": "GET /api/v1/search/emotions?q={query}",
            "color": "GET /api/v1/search/colors?q={query}",
            "generate_album": "POST /api/v1/albums-generator",
            "daily_summary": "GET /api/v1/daily-summary/{date}",
            "trends": "GET /api/v1/trends",
            "emotion_analysis": "GET /api/v1/emotion-analysis",
            "color_analysis": "GET /api/v1/color-analysis",
            "photo_analysis": "GET /api/v1/photo-analysis/{photo_id}",
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "photo-management"}

