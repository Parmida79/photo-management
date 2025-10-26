import io
import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

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

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "photo-management"}

