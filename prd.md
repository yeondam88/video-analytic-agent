Below is a sample high‐level architecture and workflow for building an **“AI-Powered Loom Video Insight System”**. After the architecture, you’ll see a brief outline for a **Product Requirements Document (PRD)** to guide development. This is designed as an **MVP** but with enough flexibility to scale up once you prove value.

---

## 1. High‐Level Architecture

### 1.1 Overview Diagram

A simplified view of the pipeline:

```
                +----------------------+
                |   Loom Videos       |
                | (source of truth)   |
                +---------+-----------+
                          | 1. Fetch + Download
                          v
                +----------------------+        +------------------+
                |  Audio Extraction   | --->   |   Local/Cloud    |
                | (e.g., ffmpeg)      |        |   Storage (S3)   |
                +---------+-----------+        +------------------+
                          | 2. Audio file
                          v
                +----------------------+        +--------------------------+
                |   Transcription     | ---->   |  transcripts table       |
                |   (Deepgram)        |        |  (raw transcript JSON)   |
                +---------+-----------+        +--------------------------+
                          | 3. Speaker diarization
                          |    + basic text cleanup
                          v
                +----------------------+        +--------------------------+
                |  Segment Creation   | ---->   |  segments table          |
                |   (python & LLM)    |        |  (start_time, end_time,  |
                +---------+-----------+        |   speaker, text, etc.)   |
                          | 4. Summaries & Titles
                          v
                +----------------------+        +--------------------------+
                |  Summaries &        | ---->   |  segments table.display_ |
                |  “Insight” Extraction|        |  text & .title fields    |
                |  (OpenAI or Claude)  |        +--------------------------+
                +---------+-----------+
                          | 5. Insert embeddings
                          v
                +----------------------+        +--------------------------+
                | Vector Embeddings    | ---->  |  segments.embedding      |
                | (OpenAI or Cohere)  |        |  PGVector (Supabase)     |
                +---------+-----------+        +--------------------------+
                          |
                          v
                +----------------------+        +--------------------------+
                |  Search & Metadata  | <----> |  MeiliSearch or PGVector |
                |  (UI + APIs)        |        +--------------------------+
                +----------------------+
```

### 1.2 Main Components

1. **Data Ingestion / Video Pipeline**

   - **Source**: Loom library (6,000+ videos).
   - **Download**: Use Loom’s API or direct links to fetch the MP4 (or similar format).
   - **Audio Extraction**: `ffmpeg` or `pydub` to strip out the audio track from video.

2. **Transcription (Deepgram)**

   - **Send audio to Deepgram**.
   - Enable **speaker diarization** (`diarization=True`).
   - Receive JSON response with:
     - Word-level timestamps
     - Speaker labels
     - Full transcript text

3. **Storage: Supabase**

   - **`videos` table** holds metadata about each Loom video (title, link, published date/time, etc.).
   - **`descriptions` (or `transcriptions`) table** for raw transcript JSON from Deepgram.
   - **`segments` table** for each monologue/turn of speech:
     - `video_id`
     - `person_id` (optional, if known; otherwise store as `speaker_0, speaker_1`, etc.)
     - `start_time`, `end_time`
     - `text` (raw from Deepgram)
     - `display_text` (punctuation and grammar corrected via LLM)
     - `title` (brief summary or topic label from LLM)
     - `metadata` (JSON with additional info if desired)
     - `embedding` (vector type from `pgvector`)

4. **Segment Creation**

   - From the raw transcript with speaker info, your Python job “chunks” that data into `segments`.
   - Each segment = a continuous block from the same speaker.
   - Example logic:
     1. Parse the Deepgram JSON word‐by‐word.
     2. If `speaker` changes, close the current segment and start a new one.
     3. Summarize or reformat text via LLM as needed.

5. **Insight Extraction & Summaries** (OpenAI or Anthropic’s Claude)

   - For each **segment** (or entire videos if short enough), pass text to an LLM.
   - You can do any of the following:
     1. **Punctuation & Grammar**: “Clean up” transcript into `display_text`.
     2. **Segment Title**: “Generate a concise, descriptive title for this segment.”
     3. **Key Insights**: “Identify any mention of frameworks, quotes, etc. Output JSON for each type.”
   - Store the results in your database (`segments` table or a separate `insights` table).

6. **Vector Embeddings**

   - Either store embeddings of the entire segment text in `segments.embedding`.
   - OR store shorter embeddings for each “insight” in a separate table.
   - Use `PGVector` in Supabase for Postgres-based vector similarity queries.

7. **Search**

   - Option A: **MeiliSearch** for keyword indexing + advanced filters.
   - Option B: **Supabase**’s built‐in `PGVector` for semantic searches.
   - Optionally combine both approaches:
     - **Keyword/filters**: MeiliSearch or Postgres FTS.
     - **Semantic**: Vector similarity on `segments.embedding`.

8. **User Interface**
   - Minimal front end to:
     - Browse videos
     - Search segments by text or embedding
     - View summarized highlights
     - Jump directly to the Loom video time range (start_time → end_time)

---

## 2. Detailed System Design Considerations

### 2.1 Data Model (Supabase/Postgres)

Below are _example_ final schemas (simplified). You can adapt as you see fit:

```sql
-- videos table
CREATE TABLE videos (
  id SERIAL PRIMARY KEY,
  loom_video_id TEXT UNIQUE NOT NULL,
  title TEXT,
  description TEXT,
  thumbnail_url TEXT,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  status TEXT,
  duration INT,
  to_process BOOLEAN DEFAULT TRUE
);

-- transcriptions (or descriptions)
CREATE TABLE transcriptions (
  id SERIAL PRIMARY KEY,
  video_id INT REFERENCES videos(id),
  raw_transcript JSONB,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- segments table
CREATE TABLE segments (
  id SERIAL PRIMARY KEY,
  video_id INT REFERENCES videos(id),
  person_id INT,  -- optional; or just store "speaker_name" TEXT
  start_time FLOAT,
  end_time FLOAT,
  text TEXT,           -- raw text from Deepgram
  display_text TEXT,   -- cleaned-up text from LLM
  title TEXT,          -- short summary from LLM
  metadata JSONB,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  deleted_at TIMESTAMP,
  embedding VECTOR(1536)  -- if using pgvector w/OpenAI 1536-dim
);
```

### 2.2 Processing Flow

1. **Ingestion**
   - For each Loom video:
     - Get metadata (title, link, date, etc.) → insert into `videos`.
     - Download MP4 → store in local server or S3.
2. **Audio Extraction**
   - Use `ffmpeg -i input.mp4 -q:a 0 -map a output.wav`.
3. **Transcription (Deepgram)**
   - Pass `output.wav` to Deepgram.
   - Get JSON w/ diarization → store in `transcriptions.raw_transcript`.
4. **Segment Generation**
   - Parse `raw_transcript`.
   - Group tokens by `speaker` to form a segment.
   - Insert into `segments` with `text`, `start_time`, `end_time`.
5. **Segment Hydration**
   - Use LLM (OpenAI GPT or Claude) to:
     1. Clean grammar → `segments.display_text`.
     2. Generate short titles → `segments.title`.
     3. (Optional) Create “insights” → separate `insights` table or store in `segments.metadata`.
6. **Embeddings**
   - `openai.Embedding.create(model="text-embedding-ada-002", input=display_text)`
   - Store the resulting embedding in `segments.embedding`.
7. **Search Index**
   - Optionally push `display_text + metadata + embedding` into MeiliSearch for fast keyword lookups.
   - Or rely on Supabase + Postgres text search + pgvector for semantic queries.
8. **Front End**
   - Provide a React/Next.js or simple Python Flask web app:
     - **Listing**: Shows all videos or segments.
     - **Search**:
       - Keywords → filter by title or text.
       - Semantic → vector similarity.
       - Display segment results, link to Loom at `start_time`.
     - **Segment Viewer**: Show “title,” “display_text,” plus an embedded Loom player starting from `start_time`.

### 2.3 Tech Stack Details

1. **Python**

   - Main orchestration language.
   - Scripts:
     - `download_videos.py` → interacts with Loom API.
     - `extract_audio.py` → uses `ffmpeg`.
     - `transcribe.py` → calls Deepgram.
     - `create_segments.py` → speaker segmentation + LLM post‐processing.
     - `embed_segments.py` → openAI embeddings + store in Supabase.
   - **pydantic v2** for data validation of pipeline inputs/outputs.

2. **Supabase**

   - Acts as the Postgres DB with pgvector extension.
   - Optionally store raw audio or video links in the DB (or references to S3).

3. **OpenAI**

   - Summaries, segment titles, and optional “insight extraction.”
   - Possibly also embeddings (unless you prefer Cohere or another vendor).

4. **Deepgram**

   - Transcription + diarization.

5. **Deployment**
   - Flexible: can host the pipeline scripts on any containerized environment (e.g., Railway, AWS Lambda if needed, etc.).
   - Host the final web UI on e.g. Vercel, Railway, or a small VM.

---

## 3. Product Requirements Document (MVP Outline)

Below is a minimal but structured PRD outline to get you started. Fill in more details as needed.

### 3.1 Product Summary

**Product Name**: Loom AI Insights  
**Goal**: Provide an internal tool for quickly searching and exploring 6,000+ Loom videos, focusing on highlighting key moments with speaker‐labeled transcripts and short summaries.

### 3.2 Key Features

1. **Video Library**

   - A simple list or gallery of available Loom videos (title, thumbnail, duration).
   - Click through to a single video’s “detail” page.

2. **Transcript & Segment Viewer**

   - Display full transcript with timestamps.
   - Show automatically segmented “speaker blocks” (monologues).
   - Each block has a short title plus cleaned text.

3. **Search**

   - Keyword search across transcript text or titles.
   - (Optional) Semantic search for more advanced queries (e.g., “customer retention discussion”).
   - Results link the user directly to the relevant timestamp in Loom.

4. **Summaries / Insights**

   - (MVP) Show a short auto‐generated summary for each segment.
   - (Future) Possibly detect “insights” or “action items” specifically.

5. **Speaker Diarization**
   - Identify each speaker in the Loom automatically (`speaker_0`, `speaker_1`, etc.).
   - (Future) If your org has known staff, a further step could match speaker_0 to known staff members.

### 3.3 Scope & Constraints

- **MVP**:
  - Only handle transcription + basic search + speaker‐segmented transcripts.
  - Summaries are short (one‐liner).
  - Focus on robust pipeline, not advanced UI.
- **Performance**:
  - 6,000 videos, average length 5–10 minutes, scale pipeline accordingly.
  - Ensure that you have enough GPU/CPU resources for transcription + LLM calls.
- **Cost**:
  - Keep an eye on Deepgram usage fees + OpenAI usage (embeddings, summarization).
  - Possibly do partial indexing (only “long videos” or “featured videos”) if cost is high.

### 3.4 Success Criteria

1. **Data Coverage**: 80%+ videos fully transcribed and stored in DB.
2. **Quality**: Summaries are helpful, minimal LLM hallucination.
3. **Search**: Users can find relevant segments in <2 seconds.
4. **User Adoption**: # of searches or # of segments viewed.

### 3.5 Timeline (MVP)

1. **Week 1–2**
   - DB schema finalization (videos, transcriptions, segments).
   - Set up Supabase with pgvector.
   - Basic pipeline code (ingestion + audio extraction + transcription).
2. **Week 3–4**
   - Segment creation + LLM summarization.
   - Store data in `segments` with embeddings.
   - Build minimal web UI (React or Next.js or Flask).
3. **Week 5**
   - Implement search (keyword + semantic).
   - Productionize pipeline.
4. **Week 6**
   - Testing & QA.
   - Deploy final system.
   - Collect feedback.

### 3.6 Future Enhancements

- Automatic speaker identity recognition (if you have a known set of voices).
- Chapter detection for entire videos (“chapters” spanning multiple segments).
- Deeper “Insight Extraction” (business frameworks, to‐dos, quotes).
- Slack integration or custom chat interface.

---

## 4. Next Steps

1. **Finalize Architecture**
   - Decide on indexing approach (MeiliSearch vs. PG full-text + vectors).
   - Create DB schema in Supabase with tables described above.
2. **Implement Pipeline**
   - Write Python scripts for each stage with pydantic for data validation.
   - Thoroughly handle exceptions (missing audio, diarization fails, etc.).
3. **Create Minimal UI**
   - Even a single “search bar” + “results page” in a web framework is enough for MVP testing.
4. **Plan for Incremental Improvement**
   - E.g., once you see usage, refine the LLM prompts, add custom logic for more interesting summaries.

With this plan, you can **start small** (get transcripts + store them + basic search) and **iterate** (speaker segmentation, summarization, advanced insights) as you see results.

Good luck building your **AI-Powered Loom Video Insight System**!
