# Configuration Guide

## Overview

The AI-Powered Photo Management Service uses a comprehensive configuration system based on Pydantic Settings. This allows for flexible configuration through environment variables, configuration files, and validation.

## Configuration Features

- **Environment Variable Support**: All settings can be overridden via environment variables
- **Validation**: Built-in validation for all configuration values
- **Environment-Specific Settings**: Different configurations for development, production, and testing
- **Type Safety**: Full type hints and validation using Pydantic
- **File Upload Management**: Configurable upload directories, file size limits, and allowed extensions
- **AI Service Configuration**: OpenAI API settings and model configurations
- **Database Configuration**: PostgreSQL and SQLite support with connection pooling
- **Redis Configuration**: For Celery task queue and caching
- **Security Settings**: JWT tokens, CORS, and rate limiting
- **Performance Tuning**: Concurrent upload limits, image processing settings

## Quick Start

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your specific settings:
   ```bash
   # Required settings
   OPENAI_API_KEY=your-openai-api-key-here
   DATABASE_URL=postgresql://user:password@localhost:5432/photo_management
   REDIS_URL=redis://localhost:6379/0
   
   # Optional settings
   DEBUG=true
   LOG_LEVEL=DEBUG
   MAX_FILE_SIZE=10485760  # 10MB
   ```

3. The application will automatically load these settings when started.

## Environment Variables

### Application Settings
- `APP_NAME`: Application name (default: "AI-Powered Photo Management Service")
- `APP_VERSION`: Application version (default: "1.0.0")
- `DEBUG`: Enable debug mode (default: false)
- `ENVIRONMENT`: Environment type - development, staging, production, testing (default: development)

### Server Settings
- `HOST`: Server host (default: "0.0.0.0")
- `PORT`: Server port (default: 8000)
- `RELOAD`: Enable auto-reload (default: false)
- `HF_PORT`: Hugging Face Spaces port (default: 7860)

### Database Settings
- `DATABASE_URL`: Database connection URL (default: postgresql://user:password@localhost:5432/photo_management)
- `DATABASE_POOL_SIZE`: Connection pool size (default: 10)
- `DATABASE_MAX_OVERFLOW`: Maximum overflow connections (default: 20)
- `DATABASE_POOL_TIMEOUT`: Pool timeout in seconds (default: 30)
- `DATABASE_POOL_RECYCLE`: Connection recycle time in seconds (default: 3600)

### Redis Settings
- `REDIS_URL`: Redis connection URL (default: redis://localhost:6379/0)
- `REDIS_HOST`: Redis host (default: localhost)
- `REDIS_PORT`: Redis port (default: 6379)
- `REDIS_DB`: Redis database number (default: 0)
- `REDIS_PASSWORD`: Redis password (optional)

### File Upload Settings
- `UPLOAD_DIR`: Directory for uploaded files (default: "./uploads")
- `MAX_FILE_SIZE`: Maximum file size in bytes (default: 10MB)
- `ALLOWED_EXTENSIONS`: Comma-separated list of allowed file extensions (default: .jpg,.jpeg,.png,.gif,.bmp,.webp,.tiff)

### AI Service Settings
- `OPENAI_API_KEY`: OpenAI API key (required for AI features)
- `AI_MODEL`: OpenAI vision model (default: gpt-4-vision-preview)
- `EMBEDDING_MODEL`: OpenAI embedding model (default: text-embedding-ada-002)
- `AI_TIMEOUT`: AI service timeout in seconds (default: 60)
- `AI_MAX_RETRIES`: Maximum retry attempts for AI calls (default: 3)

### Celery Settings
- `CELERY_BROKER_URL`: Celery broker URL (default: redis://localhost:6379/0)
- `CELERY_RESULT_BACKEND`: Celery result backend URL (default: redis://localhost:6379/0)
- `CELERY_TASK_TIME_LIMIT`: Task time limit in seconds (default: 300)
- `CELERY_TASK_SOFT_TIME_LIMIT`: Task soft time limit in seconds (default: 240)

### Security Settings
- `SECRET_KEY`: Secret key for JWT tokens (change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)
- `ALGORITHM`: JWT algorithm (default: HS256)

### CORS Settings
- `CORS_ORIGINS`: Comma-separated list of allowed origins (default: *)
- `CORS_ALLOW_CREDENTIALS`: Allow credentials (default: true)
- `CORS_ALLOW_METHODS`: Allowed HTTP methods (default: *)
- `CORS_ALLOW_HEADERS`: Allowed headers (default: *)

### Logging Settings
- `LOG_LEVEL`: Logging level - DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
- `LOG_FORMAT`: Log message format (default: %(asctime)s - %(name)s - %(levelname)s - %(message)s)
- `LOG_FILE`: Log file path (optional)

### Performance Settings
- `MAX_CONCURRENT_UPLOADS`: Maximum concurrent uploads (default: 10)
- `IMAGE_RESIZE_MAX_SIZE`: Maximum image size for processing (default: 1024,1024)
- `THUMBNAIL_SIZE`: Thumbnail size (default: 200,200)

### Cleanup Settings
- `CLEANUP_FAILED_ANALYSES_DAYS`: Days to keep failed analyses (default: 7)
- `CLEANUP_OLD_FILES_DAYS`: Days to keep old files (default: 30)

### Rate Limiting
- `RATE_LIMIT_REQUESTS_PER_MINUTE`: API requests per minute limit (default: 60)
- `RATE_LIMIT_UPLOAD_PER_HOUR`: Uploads per hour limit (default: 100)

### Monitoring Settings
- `HEALTH_CHECK_INTERVAL`: Health check interval in seconds (default: 30)
- `METRICS_ENABLED`: Enable metrics collection (default: false)
- `METRICS_PORT`: Metrics server port (default: 9090)

## Environment-Specific Configurations

### Development Environment
```bash
ENVIRONMENT=development
DEBUG=true
RELOAD=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=*
```

### Production Environment
```bash
ENVIRONMENT=production
DEBUG=false
RELOAD=false
LOG_LEVEL=WARNING
MAX_FILE_SIZE=5242880  # 5MB limit
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SECRET_KEY=your-super-secure-secret-key-for-production
```

### Testing Environment
```bash
ENVIRONMENT=testing
DEBUG=true
DATABASE_URL=sqlite:///:memory:
REDIS_URL=redis://localhost:6379/1
UPLOAD_DIR=./test_uploads
LOG_LEVEL=DEBUG
```

## Configuration Validation

The configuration system includes built-in validation:

- **File Extensions**: Automatically adds dots if missing
- **File Size**: Ensures positive values and reasonable limits
- **Database URLs**: Validates PostgreSQL and SQLite formats
- **Redis URLs**: Validates Redis connection format
- **Environment**: Validates against allowed values
- **Log Levels**: Validates against standard logging levels
- **Upload Directory**: Creates directory if missing and validates write permissions

## Usage in Code

```python
from app.config import settings

# Access configuration values
print(f"App name: {settings.app_name}")
print(f"Debug mode: {settings.debug}")
print(f"Upload directory: {settings.upload_dir}")

# Environment checks
if settings.is_production:
    print("Running in production mode")

# File validation
if settings.validate_file_extension("photo.jpg"):
    print("File extension is allowed")

# Get paths
upload_path = settings.get_upload_path("photo.jpg")
thumbnail_path = settings.get_thumbnail_path("photo.jpg")
```

## Docker Configuration

For Docker deployments, set environment variables in your docker-compose.yml:

```yaml
services:
  photo-management:
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://user:password@db:5432/photo_management
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
```

## Hugging Face Spaces

For Hugging Face Spaces deployment, the application automatically uses:
- Port 7860 (HF_PORT)
- Environment variables from the Spaces interface
- Default database and Redis configurations

## Troubleshooting

### Common Issues

1. **Upload Directory Not Writable**: Ensure the upload directory exists and has proper permissions
2. **Database Connection Failed**: Check DATABASE_URL format and database availability
3. **Redis Connection Failed**: Verify Redis is running and REDIS_URL is correct
4. **AI Analysis Failing**: Ensure OPENAI_API_KEY is set and valid
5. **CORS Issues**: Configure CORS_ORIGINS for your frontend domain

### Validation Errors

If you see validation errors, check:
- Environment variable names (should be uppercase with underscores)
- Value formats (URLs, file paths, etc.)
- Required vs optional settings
- Environment-specific restrictions

## Security Considerations

- **Never commit .env files** to version control
- **Use strong SECRET_KEY** in production
- **Restrict CORS_ORIGINS** in production
- **Use environment-specific database credentials**
- **Enable HTTPS** in production
- **Set appropriate file size limits** for your use case
- **Regularly rotate API keys** and secrets
