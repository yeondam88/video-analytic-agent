-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create helper functions
CREATE OR REPLACE FUNCTION test_vector()
RETURNS boolean
LANGUAGE plpgsql
AS $$
DECLARE
    test_vector vector(1536);
BEGIN
    -- Create a test vector
    test_vector := array_fill(0::float, ARRAY[1536]);
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$;

-- Create tables
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    loom_video_id TEXT UNIQUE NOT NULL,
    title TEXT,
    description TEXT,
    thumbnail_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending',
    duration INTEGER,
    to_process BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS transcriptions (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    raw_transcript JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS segments (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    speaker_id TEXT,
    start_time FLOAT,
    end_time FLOAT,
    text TEXT,
    display_text TEXT,
    title TEXT,
    metadata JSONB,
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Create index for vector similarity search
CREATE INDEX IF NOT EXISTS segments_embedding_idx ON segments 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Enable Row Level Security
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE segments ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Enable read access for all users" ON videos
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Enable insert access for all users" ON videos
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Enable update access for all users" ON videos
    FOR UPDATE
    TO authenticated
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Enable delete access for all users" ON videos
    FOR DELETE
    TO authenticated
    USING (true);

-- Repeat for transcriptions
CREATE POLICY "Enable read access for all users" ON transcriptions
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Enable insert access for all users" ON transcriptions
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Enable update access for all users" ON transcriptions
    FOR UPDATE
    TO authenticated
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Enable delete access for all users" ON transcriptions
    FOR DELETE
    TO authenticated
    USING (true);

-- Repeat for segments
CREATE POLICY "Enable read access for all users" ON segments
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Enable insert access for all users" ON segments
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Enable update access for all users" ON segments
    FOR UPDATE
    TO authenticated
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Enable delete access for all users" ON segments
    FOR DELETE
    TO authenticated
    USING (true); 