# Deployment Guide - Hugging Face Spaces

## Deploying AI-Powered Photo Management Service to Hugging Face Spaces

### Prerequisites
1. Hugging Face account
2. OpenAI API key
3. Git repository with the code

### Step 1: Create Hugging Face Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Fill in the details:
   - **Space name**: `ai-photo-management`
   - **License**: MIT
   - **SDK**: Docker
   - **Hardware**: CPU Basic (or GPU if needed)
   - **Visibility**: Public

### Step 2: Configure Environment Variables

In your Hugging Face Space settings, add these environment variables:

```
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/photo_management
UPLOAD_DIR=./uploads
```

### Step 3: Upload Files

Upload these files to your Hugging Face Space:

1. **Dockerfile** - Container configuration
2. **app.py** - Main application entry point
3. **requirements_hf.txt** - Python dependencies
4. **README_HF.md** - Space documentation
5. **app/** directory - Application code
6. **uploads/** directory - File storage

### Step 4: Deploy

1. Commit and push your files to the Hugging Face Space
2. The space will automatically build and deploy
3. Monitor the build logs for any issues

### Step 5: Test Deployment

Once deployed, test the following endpoints:

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /api/v1/upload` - Photo upload
- `GET /api/v1/search?q=test` - Search functionality

### File Structure for Hugging Face

```
your-space/
├── Dockerfile
├── app.py
├── requirements_hf.txt
├── README_HF.md
├── app/
│   ├── api/
│   │   ├── photos.py
│   │   ├── search.py
│   │   └── smart_features.py
│   ├── core/
│   │   └── config.py
│   ├── database/
│   │   └── models.py
│   ├── services/
│   │   └── ai_service.py
│   └── celery_app.py
└── uploads/
    └── (empty directory)
```

### Environment Configuration

The service will automatically configure itself for Hugging Face deployment:

- **Port**: 7860 (Hugging Face default)
- **Host**: 0.0.0.0 (accessible from outside)
- **Database**: PostgreSQL (configured via environment variables)
- **File Storage**: Local uploads directory

### Performance Considerations

For Hugging Face deployment:

1. **Memory Limits**: Basic CPU has 16GB RAM
2. **Storage**: 50GB persistent storage
3. **CPU**: 2 vCPU cores
4. **Timeout**: 60 seconds per request

### Monitoring and Logs

- View build logs in the Hugging Face Space interface
- Monitor application logs for errors
- Check resource usage in the Space settings

### Custom Domain (Optional)

If you have a custom domain, you can configure it in the Space settings under "Custom Domain".

### Scaling

For higher traffic or better performance:

1. Upgrade to GPU Basic or higher
2. Use external database service
3. Implement caching strategies
4. Optimize AI model usage

### Troubleshooting

Common issues and solutions:

1. **Build Failures**: Check Dockerfile and requirements
2. **Import Errors**: Verify all dependencies are included
3. **Memory Issues**: Optimize code or upgrade hardware
4. **Timeout Errors**: Implement async processing
5. **Database Connection**: Check environment variables

### Security Considerations

1. **API Keys**: Store securely in environment variables
2. **File Uploads**: Validate file types and sizes
3. **Rate Limiting**: Implement request throttling
4. **CORS**: Configure appropriate origins

### Maintenance

Regular maintenance tasks:

1. **Update Dependencies**: Keep packages up to date
2. **Monitor Logs**: Check for errors and performance issues
3. **Backup Data**: Regular database backups
4. **Security Updates**: Apply security patches promptly

This deployment guide ensures your AI-Powered Photo Management Service runs smoothly on Hugging Face Spaces with optimal performance and reliability.
