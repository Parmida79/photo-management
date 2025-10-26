#!/usr/bin/env python3
"""
Startup script for the AI-Powered Photo Management Service
"""

import os
import sys
import subprocess
from pathlib import Path

from app import settings


def check_requirements():
    """Check if all required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        import celery
        import redis
        import openai
        import sqlalchemy
        import pillow
        import numpy
        import sklearn
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False


def check_environment():
    """Check if environment variables are set."""
    env_file = Path("../.env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False

    # Check if OpenAI API key is set
    from dotenv import load_dotenv
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set in .env file")
        return False

    print("✅ Environment variables configured")
    return True


def check_redis():
    """Check if Redis is running."""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running")
        return True
    except Exception as e:
        print(f"❌ Redis is not running: {e}")
        print("Please start Redis server:")
        print("  Windows: redis-server")
        print("  macOS/Linux: sudo systemctl start redis")
        return False


def create_directories():
    """Create necessary directories."""
    upload_dir = Path("../uploads")
    upload_dir.mkdir(exist_ok=True)
    print("✅ Upload directory created")


def start_celery_worker():
    """Start Celery worker in background."""
    try:
        # Start Celery worker
        cmd = ["celery", "-A", "app.celery_app", "worker", "--loglevel=info", "--detach"]
        subprocess.run(cmd, check=True)
        print("✅ Celery worker started")
        return True
    except Exception as e:
        print(f"❌ Failed to start Celery worker: {e}")
        print("   Make sure Celery is installed: pip install celery")
        return False


def start_fastapi():
    """Start FastAPI application."""
    try:
        print("🚀 Starting AI-Powered Photo Management Service...")
        print("📡 API will be available at: http://localhost:8000")
        print("📚 API documentation at: http://localhost:8000/docs")
        print("🛑 Press Ctrl+C to stop the service")

        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            log_level=settings.log_level,
            reload=settings.reload,
        )
    except KeyboardInterrupt:
        print("\n🛑 Service stopped by user")
    except Exception as e:
        print(f"❌ Failed to start FastAPI: {e}")


def main():
    """Main startup function."""
    print("🔍 AI-Powered Photo Management Service - Startup Check")
    print("=" * 60)

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Check environment
    if not check_environment():
        sys.exit(1)

    # Check Redis
    if not check_redis():
        sys.exit(1)

    # Create directories
    create_directories()

    # Start Celery worker
    if not start_celery_worker():
        print("❌ Celery worker is required for photo analysis")
        print("   Please install Celery: pip install celery")
        print("   And start Redis: redis-server")
        sys.exit(1)

    print("=" * 60)

    # Start FastAPI
    start_fastapi()


if __name__ == "__main__":
    main()
