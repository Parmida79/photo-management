"""
Configuration module for AI-Powered Photo Management Service.

This module provides centralized configuration management using Pydantic Settings,
supporting environment variables, configuration files, and validation.
"""

import os
from typing import List, Optional
from pathlib import Path
from pydantic import Field, validator
from pydantic_settings import BaseSettings as PydanticBaseSettings


class Settings(PydanticBaseSettings):
    """
    Application settings with environment variable support.

    All settings can be overridden via environment variables.
    Environment variables should be uppercase with underscores.
    """

    # Application Settings
    app_name: str = Field(default="AI-Powered Photo Management Service", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Server Settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    reload: bool = Field(default=True, env="RELOAD")
    log_level: str = Field(default="info", env="LOG_LEVEL")

    # Hugging Face Spaces specific settings
    huggingface_port: int = Field(default=7860, env="HF_PORT")

    # Database Settings
    database_url: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/photo_management",
        env="DATABASE_URL"
    )
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    database_pool_timeout: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    database_pool_recycle: int = Field(default=3600, env="DATABASE_POOL_RECYCLE")

    # Redis Settings (for Celery)
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")

    # File Upload Settings
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    max_file_size: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    allowed_extensions: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"],
        env="ALLOWED_EXTENSIONS"
    )

    # AI Service Settings
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ai_model: str = Field(default="gpt-4-vision-preview", env="AI_MODEL")
    embedding_model: str = Field(default="text-embedding-ada-002", env="EMBEDDING_MODEL")
    ai_timeout: int = Field(default=60, env="AI_TIMEOUT")
    ai_max_retries: int = Field(default=3, env="AI_MAX_RETRIES")

    # Celery Settings
    celery_broker_url: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    celery_task_serializer: str = Field(default="json", env="CELERY_TASK_SERIALIZER")
    celery_accept_content: List[str] = Field(default=["json"], env="CELERY_ACCEPT_CONTENT")
    celery_result_serializer: str = Field(default="json", env="CELERY_RESULT_SERIALIZER")
    celery_timezone: str = Field(default="UTC", env="CELERY_TIMEZONE")
    celery_task_time_limit: int = Field(default=300, env="CELERY_TASK_TIME_LIMIT")  # 5 minutes
    celery_task_soft_time_limit: int = Field(default=240, env="CELERY_TASK_SOFT_TIME_LIMIT")  # 4 minutes
    celery_worker_prefetch_multiplier: int = Field(default=1, env="CELERY_WORKER_PREFETCH_MULTIPLIER")
    celery_worker_max_tasks_per_child: int = Field(default=50, env="CELERY_WORKER_MAX_TASKS_PER_CHILD")

    # Security Settings
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    algorithm: str = Field(default="HS256", env="ALGORITHM")

    # CORS Settings
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")

    # Logging Settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")

    # Performance Settings
    max_concurrent_uploads: int = Field(default=10, env="MAX_CONCURRENT_UPLOADS")
    image_resize_max_size: tuple = Field(default=(1024, 1024), env="IMAGE_RESIZE_MAX_SIZE")
    thumbnail_size: tuple = Field(default=(200, 200), env="THUMBNAIL_SIZE")

    # Cleanup Settings
    cleanup_failed_analyses_days: int = Field(default=7, env="CLEANUP_FAILED_ANALYSES_DAYS")
    cleanup_old_files_days: int = Field(default=30, env="CLEANUP_OLD_FILES_DAYS")

    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(default=60, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    rate_limit_upload_per_hour: int = Field(default=100, env="RATE_LIMIT_UPLOAD_PER_HOUR")

    # Monitoring and Health Checks
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    metrics_enabled: bool = Field(default=False, env="METRICS_ENABLED")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("upload_dir")
    def validate_upload_dir(cls, v):
        """Ensure upload directory exists and is writable."""
        upload_path = Path(v)
        upload_path.mkdir(parents=True, exist_ok=True)

        if not upload_path.is_dir():
            raise ValueError(f"Upload directory {v} is not a valid directory")

        if not os.access(upload_path, os.W_OK):
            raise ValueError(f"Upload directory {v} is not writable")

        return str(upload_path.absolute())

    @validator("allowed_extensions")
    def validate_allowed_extensions(cls, v):
        """Ensure all extensions start with a dot."""
        return [ext if ext.startswith('.') else f'.{ext}' for ext in v]

    @validator("max_file_size")
    def validate_max_file_size(cls, v):
        """Ensure max file size is reasonable."""
        if v <= 0:
            raise ValueError("Max file size must be positive")
        if v > 100 * 1024 * 1024:  # 100MB
            raise ValueError("Max file size cannot exceed 100MB")
        return v

    @validator("database_url")
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v.startswith(("postgresql://", "postgres://", "sqlite:///")):
            raise ValueError("Database URL must be PostgreSQL or SQLite")
        return v

    @validator("redis_url")
    def validate_redis_url(cls, v):
        """Validate Redis URL format."""
        if not v.startswith("redis://"):
            raise ValueError("Redis URL must start with redis://")
        return v

    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment setting."""
        allowed_envs = ["development", "staging", "production", "testing"]
        if v not in allowed_envs:
            raise ValueError(f"Environment must be one of: {allowed_envs}")
        return v

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of: {allowed_levels}")
        return v.upper()

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == "testing"

    @property
    def redis_url_with_password(self) -> str:
        """Get Redis URL with password if provided."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def celery_broker_url_with_password(self) -> str:
        """Get Celery broker URL with password if provided."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    def get_cors_origins(self) -> List[str]:
        """Get CORS origins, handling wildcard and environment-specific settings."""
        if "*" in self.cors_origins:
            return ["*"]

        if self.is_production:
            # In production, be more restrictive
            return [origin for origin in self.cors_origins if origin != "*"]

        return self.cors_origins

    def get_database_url_for_env(self) -> str:
        """Get database URL appropriate for current environment."""
        if self.is_testing:
            # Use in-memory SQLite for testing
            return "sqlite:///:memory:"

        return self.database_url

    def get_upload_path(self, filename: str) -> str:
        """Get full path for uploaded file."""
        return str(Path(self.upload_dir) / filename)

    def get_thumbnail_path(self, filename: str) -> str:
        """Get full path for thumbnail file."""
        name, ext = os.path.splitext(filename)
        thumbnail_filename = f"{name}_thumb{ext}"
        return str(Path(self.upload_dir) / "thumbnails" / thumbnail_filename)

    def validate_file_extension(self, filename: str) -> bool:
        """Validate if file extension is allowed."""
        _, ext = os.path.splitext(filename.lower())
        return ext in self.allowed_extensions

    def validate_file_size(self, file_size: int) -> bool:
        """Validate if file size is within limits."""
        return file_size <= self.max_file_size


# Global settings instance
settings = Settings()


# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings."""
    debug: bool = True
    reload: bool = True
    log_level: str = "DEBUG"
    cors_origins: List[str] = ["*"]


class ProductionSettings(Settings):
    """Production environment settings."""
    debug: bool = False
    reload: bool = False
    log_level: str = "WARNING"
    cors_origins: List[str] = []  # Should be set via environment variables
    max_file_size: int = 5 * 1024 * 1024  # 5MB limit in production


class TestingSettings(Settings):
    """Testing environment settings."""
    debug: bool = True
    database_url: str = "sqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/1"  # Use different DB for tests
    upload_dir: str = "./test_uploads"
    log_level: str = "DEBUG"


def get_settings() -> Settings:
    """
    Get settings instance based on environment.

    Returns:
        Settings instance appropriate for current environment
    """
    env = os.getenv("ENVIRONMENT", "development").lower()

    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Export the main settings instance
__all__ = ["Settings", "settings", "get_settings", "DevelopmentSettings", "ProductionSettings", "TestingSettings"]
