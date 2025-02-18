# Video Analytics API Documentation

## Overview

The Video Analytics API is a powerful service that processes and analyzes video content using AI. It provides features for video transcription, speaker diarization, content summarization, and semantic search.

## Features

- Video Processing
  - Automatic video download and processing
  - Audio extraction and normalization
  - Support for multiple video formats
- Transcription & Analysis
  - High-accuracy speech-to-text using Deepgram
  - Speaker diarization and identification
  - Content segmentation by topic/speaker
- AI-Powered Insights
  - Content summarization using GPT-4
  - Key points extraction
  - Sentiment analysis
- Search & Discovery
  - Semantic search using embeddings
  - Vector similarity search with pgvector
  - Full-text search capabilities

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL with pgvector extension
- FFmpeg
- Supabase account
- OpenAI API key
- Deepgram API key

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/video-analytics-api.git
   cd video-analytics-api
   ```

2. Create and activate virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:
   ```bash
   alembic upgrade head
   ```

### Running the API

Development server:

```bash
uvicorn src.api.main:app --reload
```

Production server:

```bash
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## API Documentation

The API documentation is available at:

- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

## Project Structure

```
video-analytic-agent/
├── config/             # Global configuration files
├── src/               # Source code
│   ├── api/          # FastAPI application
│   │   ├── alembic/  # Database migrations
│   │   ├── config/   # API-specific configuration
│   │   ├── core/     # Core functionality
│   │   ├── dependencies/ # FastAPI dependencies
│   │   ├── middleware/   # Custom middleware
│   │   ├── routers/  # API route handlers
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic services
│   │   └── templates/ # HTML templates
│   ├── db/          # Database layer
│   │   ├── models/  # SQLAlchemy models
│   │   ├── migrations/ # Database migrations
│   │   └── utils/   # Database utilities
│   ├── pipeline/    # Video processing pipeline
│   │   ├── audio/   # Audio extraction
│   │   ├── segmentation/ # Video segmentation
│   │   ├── transcription/ # Speech-to-text
│   │   └── video/   # Video processing
│   └── web/         # React web interface
├── tests/            # Test files
│   ├── unit/       # Unit tests
│   ├── integration/ # Integration tests
│   └── e2e/        # End-to-end tests
├── storage/          # Local storage for videos and audio
│   ├── videos/     # Downloaded video files
│   └── audio/      # Extracted audio files
└── docs/            # Documentation
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_video_service.py

# Run with coverage report
pytest --cov=src tests/
```

### Code Style

We use:

- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

Run all checks:

```bash
./scripts/lint.sh
```

### Making Changes

1. Create a new branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:

   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

3. Push and create a pull request:
   ```bash
   git push origin feature/your-feature-name
   ```

## Deployment

### Docker

Build the image:

```bash
docker build -t video-analytics-api .
```

Run the container:

```bash
docker run -p 8000:8000 video-analytics-api
```

### Environment Variables

Required environment variables:

- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase project key
- `OPENAI_API_KEY`: OpenAI API key
- `DEEPGRAM_API_KEY`: Deepgram API key

Optional environment variables:

- `ENVIRONMENT`: development/production (default: development)
- `API_DEBUG`: Enable debug mode (default: false)
- `API_WORKERS`: Number of worker processes (default: 1)
- `MAX_STORAGE_GB`: Maximum storage size in GB (default: 5)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
