# AI-Powered Loom Video Insight System

A system for processing and analyzing Loom videos with AI-powered features including transcription, segmentation, summarization, and semantic search.

## Features

- Video Library Management
- Transcript & Segment Viewer
- Search Functionality (keyword + semantic)
- Summaries/Insights
- Speaker Diarization

## Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd video-analytic-agent
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your actual API keys and configuration
```

5. Set up Supabase:

- Create a new Supabase project
- Enable the `pgvector` extension
- Run the schema.sql script in the SQL editor
- Copy your project URL and anon key to .env

## Development

The project structure is organized as follows:

```
video-analytic-agent/
├── config/             # Configuration files
├── src/               # Source code
│   ├── api/          # FastAPI application
│   ├── pipeline/     # Video processing pipeline
│   ├── db/           # Database models and migrations
│   └── web/          # Web interface
├── tests/             # Test files
├── storage/           # Local storage for videos and audio
│   ├── videos/       # Downloaded video files
│   └── audio/        # Extracted audio files
└── requirements.txt   # Python dependencies
```

## Required API Keys

- Supabase: For database and storage
- Deepgram: For audio transcription
- OpenAI: For summarization and embeddings

## License

[MIT License](LICENSE)
