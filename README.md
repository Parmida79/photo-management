# AI-Powered Photo Management Service
A cloud-based photo management service built with FastAPI that provides AI-powered analysis, semantic search, and intelligent features for photo organization and discovery.

## Features

### Core Features
- **Photo Upload**: Secure file upload with validation and storage
- **AI Analysis**: Automatic generation of tags, captions, and embeddings for each photo
- **Semantic Search**: Find photos by meaning using AI-generated embeddings
- **Smart Features**: AI-powered album generation, daily summaries, and trend analysis

### AI-Powered Features (Mandatory)
- **Image Analysis**: GPT-4 Vision for tags and captions
- **Emotion Detection**: AI analysis of emotional content in photos
- **Color Analysis**: Automatic extraction of dominant colors and palettes
- **Semantic Search**: Vector-based similarity search using embeddings
- **Smart Albums**: AI-generated photo collections based on themes
- **Daily Summaries**: AI-generated insights about daily photo patterns
- **Trend Analysis**: AI-powered analysis of photo trends over time

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite (with SQLAlchemy ORM)
- **AI Services**: OpenAI GPT-4 Vision, GPT-3.5 Turbo, Text Embeddings
- **Async Processing**: Celery with Redis
- **Image Processing**: Pillow (PIL)
- **Vector Similarity**: scikit-learn cosine similarity

## Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd photo_management_service
```

2. **Python3.X**:

```bash
cd /tmp/
wget https://www.python.org/ftp/python/3.11.11/Python-3.11.11.tgz
tar xzf Python-3.11.11.tgz
cd Python-3.11.11
sudo ./configure --enable-optimizations
sudo make -j "$(nproc)"
sudo make altinstall
sudo rm /tmp/Python-3.11.11.tgz
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. Set virtualenv wrapper
```bash
```bash
sudo pip3.11 install -U pip setuptools wheel
sudo pip3.11 install virtualenvwrapper

echo "export VIRTUALENVWRAPPER_PYTHON=`which python3.8`" >> ~/.bashrc
echo "alias v.activate=\"source $(which virtualenvwrapper.sh)\"" >> ~/.bashrc
source ~/.bashrc
v.activate
mkvirtualenv --python=$(which python3.8) invoker
```

5. ***Create Database and Schema***:
```bash
python -m app.cli create-schema
```

6. **Set up environment variables**:
```bash
# Create .env file
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
echo "DATABASE_URL=sqlite:///./photo_management.db" >> .env
echo "REDIS_URL=redis://localhost:6379/0" >> .env
```

7. **Start Redis** (for Celery):
```bash
# On Windows
redis-server

# On macOS/Linux
sudo systemctl start redis
```

8. **Start the application** (includes Celery worker):
```bash
python start_service.py
```

### Run the project using uvicorn
```bash
uvicorn app.main:app --reload
```

**Note**: The startup script will automatically start the Celery worker. For manual control, you can start it separately:
```bash
celery -A app.celery_app worker --loglevel=info
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Photo Management
- `POST /api/v1/upload` - Upload a photo and trigger AI analysis
- `GET /api/v1/photo/{photo_id}` - Get photo metadata and AI analysis
- `GET /api/v1/photos` - List all photos with pagination
- `GET /api/v1/photo/{photo_id}/status` - Check analysis status
- `DELETE /api/v1/photo/{photo_id}` - Delete a photo

### Search
- `GET /api/v1/search?q={query}` - Semantic search using AI embeddings
- `GET /api/v1/search/tags?tags={tags}` - Search by tags
- `GET /api/v1/search/emotions?emotion={emotion}` - Search by emotions
- `GET /api/v1/search/colors?color={color}` - Search by colors

### Smart Features
- `POST /api/v1/albums/generate?theme={theme}` - Generate AI-powered album
- `GET /api/v1/daily-summary/{date}` - Get AI-generated daily summary
- `GET /api/v1/trends` - Analyze photo trends over time
- `GET /api/v1/emotion-analysis` - Comprehensive emotion analysis
- `GET /api/v1/color-analysis` - Comprehensive color analysis

## Usage Examples

### Upload a Photo
```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_photo.jpg"
```

### Search Photos
```bash
# Semantic search
curl "http://localhost:8000/api/v1/search?q=sunset%20beach"

# Search by emotion
curl "http://localhost:8000/api/v1/search/emotions?emotion=happy"

# Search by color
curl "http://localhost:8000/api/v1/search/colors?color=blue"
```

### Generate Smart Album
```bash
curl -X POST "http://localhost:8000/api/v1/albums/generate?theme=nature&max_photos=10"
```

### Get Daily Summary
```bash
curl "http://localhost:8000/api/v1/daily-summary/2024-01-15"
```

## AI Integration Details

### Models Used
- **GPT-4 Vision Preview**: Image analysis for tags and captions
- **Text Embedding Ada-002**: Generating embeddings for semantic search
- **GPT-3.5 Turbo**: Text generation for smart features

### AI Analysis Process
1. **Upload**: Photo uploaded and stored
2. **Analysis**: AI generates tags, caption, and embedding
3. **Storage**: Results stored in database
4. **Search**: Embeddings used for semantic similarity

### Smart Features
- **Album Generation**: AI groups photos by theme using embeddings
- **Daily Summaries**: AI analyzes daily photo patterns and emotions
- **Trend Analysis**: AI identifies patterns over time
- **Emotion Analysis**: AI detects emotional content in photos
- **Color Analysis**: AI extracts dominant colors and palettes

## Database Schema

### Photos Table
- `id`: Unique photo identifier
- `filename`: Stored filename
- `original_filename`: Original upload filename
- `file_path`: Path to stored file
- `upload_date`: Upload timestamp
- `caption`: AI-generated caption
- `tags`: AI-generated tags (JSON array)
- `embedding`: AI-generated embedding vector (JSON)
- `analysis_status`: Analysis status (pending/processing/completed/failed)

### Emotion Analysis Table
- `photo_id`: Reference to photo
- `emotions`: Emotion scores (JSON)
- `dominant_emotion`: Most prominent emotion
- `confidence_score`: AI confidence level

### Color Analysis Table
- `photo_id`: Reference to photo
- `dominant_colors`: Top colors with percentages (JSON)
- `brightness`: Overall brightness score
- `saturation`: Overall saturation score

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for AI services
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection for Celery
- `UPLOAD_DIR`: Directory for photo storage
- `MAX_FILE_SIZE`: Maximum file size (bytes)

### AI Settings
- `AI_MODEL`: Vision model name
- `EMBEDDING_MODEL`: Embedding model name
- `MAX_TAGS`: Maximum tags per photo
- `CAPTION_MAX_LENGTH`: Maximum caption length

## Performance Considerations

### Async Processing
- Photo analysis runs in background using Celery
- API responds immediately after upload
- Analysis status tracked in database

### Search Optimization
- Embeddings cached in database
- Cosine similarity for fast matching
- Configurable similarity thresholds
- Pagination for large result sets

### Scalability
- Horizontal scaling with multiple Celery workers
- Database indexing on analysis status
- Redis for task queue management
- File storage can be moved to cloud storage

## Error Handling

### AI Service Failures
- Graceful degradation with fallback responses
- Mock data when AI services unavailable
- Retry mechanisms for transient failures
- Comprehensive error logging

### File Handling
- File type validation
- Size limit enforcement
- Secure file storage
- Cleanup on failures

## Monitoring and Logging

### AI Usage Tracking
- Analysis success/failure rates
- Processing times
- API usage metrics
- Error patterns

### Performance Metrics
- Upload processing time
- Search response times
- AI analysis duration
- Database query performance

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Code Structure
```
app/
│   ├── api/        # API endpoints
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── photos.py          # Upload/retrieve/delete for v1
│   │   │   └── analyze.py         # Analyze endpoint for v1
├── filters/        # Filters
├── models/         # Database models
├── schemas/        # Pydantic models for responses
├── services/       # AI services
├── tests/          # Tests
└── utils
│    ├── __init__.py
│    ├── helpers.py  # Defines functions for validations and AI features.
│    └── mixins.py      # Defines functions for mixins.
└── celery_app.py   # Async processing
└── cli.py          # Async processing
└── config.py       # Settings
└── db.py           # Database Configs
└── main.py         # Initializes the FastAPI application.
```

### Adding New Features
1. Create models `app/models`
2. Add API endpoints in `app/api/`
3. Implement AI services in `app/services/`
4. Add Celery tasks for async processing
5. Update documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions:
- Create an issue in the repository
- Check the AI Usage Documentation
- Review the API documentation at `/docs` when running the service
