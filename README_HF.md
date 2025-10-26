---
title: AI-Powered Photo Management Service
emoji: 📸
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
short_description: AI-powered photo management with semantic search and smart features
---

# AI-Powered Photo Management Service

A cloud-based photo management service that uses AI to analyze photos, generate tags and captions, and provide semantic search capabilities.

## Features

- **AI Photo Analysis**: Automatic tag generation, captions, and embeddings
- **Semantic Search**: Find photos by meaning using AI embeddings
- **Smart Features**: AI-generated albums, daily summaries, and trend analysis
- **Emotion Detection**: AI analysis of emotional content in photos
- **Color Analysis**: Automatic extraction of dominant colors

## API Endpoints

- `POST /api/v1/upload` - Upload a photo
- `GET /api/v1/photo/{id}` - Get photo metadata
- `GET /api/v1/search?q={query}` - Semantic search
- `POST /api/v1/albums/generate` - Generate AI-powered albums
- `GET /api/v1/daily-summary/{date}` - Get daily summaries

## Technology Stack

- FastAPI (Python)
- OpenAI GPT-4 Vision
- PostgreSQL
- Redis
- Celery for async processing

## Usage

1. Upload photos using the `/api/v1/upload` endpoint
2. Search photos semantically using `/api/v1/search`
3. Generate smart albums with `/api/v1/albums/generate`
4. Get daily summaries with `/api/v1/daily-summary/{date}`

## Environment Variables

Set your OpenAI API key in the environment variables section of this Space.
