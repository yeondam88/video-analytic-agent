# Video Analytics System: Architecture & Flow

## System Overview

The video analytics system is designed to process video content through a modular pipeline, extracting audio, generating transcripts, segmenting content, and providing AI-powered insights. The system enables users to search, analyze, and interact with video content in powerful ways.

## Architecture Overview

The system follows a modular, pipeline-based architecture that processes videos through several sequential stages, from URL submission to searchable, segmented content with AI-generated insights.

### Core Components

1. **Frontend (React)**
   - User interface for submitting video URLs (YouTube, Loom)
   - Video playback and navigation
   - Transcript and segment exploration
   - Search functionality
   - Progress tracking and status monitoring

2. **API Layer (FastAPI)**
   - RESTful endpoints for video processing, retrieval and search
   - Background task management
   - Error handling and validation

3. **Database (PostgreSQL)**
   - Stores video metadata, transcripts, segments, and embeddings
   - Uses pgvector for vector similarity search
   - Managed through SQLAlchemy ORM

4. **Pipeline System**
   - Multi-stage processing with status tracking
   - Error handling and retries
   - Progress reporting

## Data Flow

1. **Video Submission**
   - User submits YouTube/Loom URL through frontend
   - API validates URL and creates a database entry
   - Background task initiates processing

2. **Processing Pipeline**
   - **Stage 1: Download & Audio Extraction**
     - VideoDownloader pulls video from source
     - AudioExtractor extracts WAV audio (mono, 16kHz)
     - Status updates sent to database
   
   - **Stage 2: Transcription**
     - DeepgramTranscriber sends audio to Deepgram API
     - Processes response with word timing and speaker data
     - Saves transcript to database
   
   - **Stage 3: Segmentation**
     - SegmentProcessor divides transcript into logical segments
     - Generates embeddings for each segment using OpenAI API
     - Creates segment summaries using GPT-4
     - Saves segments to database with vector embeddings

3. **User Interaction**
   - Frontend polls for status updates
   - Once complete, user can browse video, transcript, and segments
   - Search functionality using vector similarity

## System Flow Diagram

```mermaid
flowchart TD
    %% User Flow
    User([User]) -->|Submit Video URL| WebUI

    %% Main Components
    subgraph Frontend
        WebUI[React Web Interface]
        VideoPlayer[Video Player]
        SegmentViewer[Segment Viewer]
        TranscriptViewer[Transcript Viewer]
        SearchInterface[Search Interface]
    end

    subgraph API ["API Layer (FastAPI)"]
        VideoEndpoint[/videos Endpoint/]
        SearchEndpoint[/search Endpoint/]
        SegmentEndpoint[/segments Endpoint/]
        QueueEndpoint[/queue Endpoint/]
    end

    subgraph Pipeline ["Video Processing Pipeline"]
        Coordinator[Pipeline Coordinator]
        
        subgraph Stage1 ["Stage 1: Download & Extraction"]
            Downloader[Video Downloader]
            AudioExtractor[Audio Extractor]
        end
        
        subgraph Stage2 ["Stage 2: Transcription"]
            Transcriber[Deepgram Transcriber]
        end
        
        subgraph Stage3 ["Stage 3: Segmentation"]
            Segmenter[Segment Processor]
            Embedder[OpenAI Embeddings]
            Summarizer[GPT-4 Summaries]
        end
    end

    subgraph Database ["Database (PostgreSQL)"]
        VideosTable[(Videos)]
        TranscriptionsTable[(Transcriptions)]
        SegmentsTable[(Segments)]
        QueueTable[(Queue)]
    end

    subgraph ExternalServices ["External Services"]
        YoutubeAPI[YouTube API]
        LoomAPI[Loom API]
        DeepgramAPI[Deepgram API]
        OpenAIAPI[OpenAI API]
    end

    subgraph Storage ["File Storage"]
        VideoFiles[(Video Files)]
        AudioFiles[(Audio Files)]
    end

    %% Connections - Frontend to API
    WebUI -->|Submit URL| VideoEndpoint
    WebUI -->|Poll Status| VideoEndpoint
    WebUI -->|Query| SearchEndpoint
    SegmentViewer -->|Fetch Segments| SegmentEndpoint
    TranscriptViewer -->|Fetch Transcript| VideoEndpoint
    VideoPlayer -->|Fetch Video Data| VideoEndpoint
    SearchInterface -->|Search Query| SearchEndpoint

    %% Connections - API to Pipeline
    VideoEndpoint -->|Process Video| Coordinator
    QueueEndpoint -->|Queue Items| Coordinator

    %% Pipeline Internal Flow
    Coordinator -->|Start Download| Downloader
    Downloader -->|Source ID| YoutubeAPI
    Downloader -->|Source ID| LoomAPI
    Downloader -->|Save Video| VideoFiles
    Downloader -->|Update Status| VideosTable
    
    Downloader -->|Start Extraction| AudioExtractor
    AudioExtractor -->|Read Video| VideoFiles
    AudioExtractor -->|Save Audio| AudioFiles
    AudioExtractor -->|Update Status| VideosTable
    
    AudioExtractor -->|Start Transcription| Transcriber
    Transcriber -->|Send Audio| DeepgramAPI
    Transcriber -->|Save Transcript| TranscriptionsTable
    Transcriber -->|Update Status| VideosTable
    
    Transcriber -->|Start Segmentation| Segmenter
    Segmenter -->|Generate Embeddings| Embedder
    Embedder -->|API Call| OpenAIAPI
    Segmenter -->|Generate Summaries| Summarizer
    Summarizer -->|API Call| OpenAIAPI
    Segmenter -->|Save Segments| SegmentsTable
    Segmenter -->|Update Status| VideosTable

    %% API to Database
    VideoEndpoint -->|Query/Update| VideosTable
    VideoEndpoint -->|Query| TranscriptionsTable
    SegmentEndpoint -->|Query| SegmentsTable
    SearchEndpoint -->|Vector Search| SegmentsTable
    QueueEndpoint -->|Manage| QueueTable

    %% Status Flow
    VideosTable -->|Status Updates| WebUI

    %% Styling
    classDef frontend fill:#d4f1f9,stroke:#0384fc,stroke-width:2px
    classDef api fill:#ffe6cc,stroke:#d79b00,stroke-width:2px
    classDef pipeline fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    classDef database fill:#f8cecc,stroke:#b85450,stroke-width:2px
    classDef external fill:#e1d5e7,stroke:#9673a6,stroke-width:2px
    classDef storage fill:#fff2cc,stroke:#d6b656,stroke-width:2px
    classDef stage fill:#d5e8d4,stroke:#82b366,stroke-width:1px,stroke-dasharray: 5 5

    class Frontend,WebUI,VideoPlayer,SegmentViewer,TranscriptViewer,SearchInterface frontend
    class API,VideoEndpoint,SearchEndpoint,SegmentEndpoint,QueueEndpoint api
    class Pipeline,Coordinator,Downloader,AudioExtractor,Transcriber,Segmenter,Embedder,Summarizer pipeline
    class Database,VideosTable,TranscriptionsTable,SegmentsTable,QueueTable database
    class ExternalServices,YoutubeAPI,LoomAPI,DeepgramAPI,OpenAIAPI external
    class Storage,VideoFiles,AudioFiles storage
    class Stage1,Stage2,Stage3 stage
```

## Key Data Models

1. **Video**
   - Stores metadata (title, description, duration)
   - Tracks processing status and progress
   - References transcripts and segments

2. **Transcription**
   - Stores raw Deepgram response
   - Includes word-level timing and speaker data

3. **Segment**
   - Contains text content with start/end times
   - Stores vector embeddings (1536 dimensions)
   - Has additional metadata like speaker ID and titles

4. **Queue**
   - Manages video processing queue
   - Handles priorities and bulk uploads

## Technical Components

1. **External Services**
   - **Deepgram**: Speech-to-text API (nova-2 model)
   - **OpenAI**: Embeddings (text-embedding-3-small) and summaries (GPT-4)
   - **YouTube/Loom**: Video sources

2. **Key Libraries**
   - yt-dlp for YouTube downloads
   - FFmpeg for audio extraction
   - pgvector for vector search
   - SQLAlchemy for database ORM
   - FastAPI for backend API
   - React for frontend

3. **Error Handling**
   - Exponential backoff for retries
   - Detailed error logging
   - Status updates to database

4. **Progress Tracking**
   - Fine-grained progress per stage (0-100%)
   - Status enums (PENDING → DOWNLOADING → ... → COMPLETED)
   - Step completion tracking

## System Design Principles

1. **Modularity**
   - Each pipeline stage is independent
   - Separation of concerns between components

2. **Scalability**
   - Background processing of videos
   - Queue system for handling multiple videos
   - Processing status tracking

3. **Robustness**
   - Error handling at each stage
   - Retries with exponential backoff
   - Detailed error logging

4. **User Experience**
   - Real-time progress updates
   - Interactive segment navigation
   - Rich search capabilities
   - Minimal UI with loading states

## Processing Status Flow

```
PENDING → DOWNLOADING → DOWNLOADED →
EXTRACTING_AUDIO → AUDIO_EXTRACTED →
TRANSCRIBING → TRANSCRIBED →
SEGMENTING → COMPLETED
```

## Progress Calculation

```
Download: 0-20%
Audio Extraction: 20-40%
Transcription: 40-60%
Segmentation: 60-80%
Processing: 80-100%
```
