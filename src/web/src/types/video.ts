export enum VideoStatus {
  PENDING = "PENDING",
  DOWNLOADING = "DOWNLOADING",
  DOWNLOADED = "DOWNLOADED",
  EXTRACTING_AUDIO = "EXTRACTING_AUDIO",
  AUDIO_EXTRACTED = "AUDIO_EXTRACTED",
  TRANSCRIBING = "TRANSCRIBING",
  TRANSCRIBED = "TRANSCRIBED",
  SEGMENTING = "SEGMENTING",
  PROCESSING = "PROCESSING",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED"
}

export enum VideoSource {
  LOOM = "LOOM",
  YOUTUBE = "YOUTUBE",
  LOCAL = "LOCAL"
}

interface ProcessingStep {
  step: string;
  timestamp: string;
  status: string;
  progress: number;
  error?: string;
}

export interface Video {
  id: string;
  url: string;
  title: string | null;
  description?: string;
  source: VideoSource;
  source_id: string;
  status: VideoStatus;
  progress: number;
  error?: string;
  steps_completed: string[];
  processing_details: ProcessingStep[];
  created_at: string;
  updated_at?: string;
  thumbnail_url?: string;
  metadata?: {
    summary?: string;
    key_points?: string[];
  };
}

export interface BaseVideo {
  title: string;
  url: string;
  thumbnail_url: string;
  duration: number;
  created_at: string;
  status: VideoStatus;
  progress: number;
  steps_completed: string[];
  error: string | null;
}

export interface VideoResponse extends BaseVideo {
  id: number; // API returns number, but we convert to string for frontend use
}

export interface Segment {
  id: string;
  video_id: string;
  start_time: number;
  end_time: number;
  text: string;
  display_text?: string;
  speaker_id: string;
  confidence: number;
  words: Array<{
    word: string;
    start: number;
    end: number;
    confidence: number;
  }>;
  created_at?: string;
  updated_at?: string;
}

export type ProcessingStepType = {
  id: string;
  label: string;
  description: string;
};

export const processingSteps: ProcessingStepType[] = [
  {
    id: 'downloading',
    label: 'Downloading Video',
    description: 'Downloading video from source'
  },
  {
    id: 'extracting_audio',
    label: 'Extracting Audio',
    description: 'Extracting audio from video file'
  },
  {
    id: 'transcribing',
    label: 'Transcribing',
    description: 'Converting speech to text'
  },
  {
    id: 'segmenting',
    label: 'Segmenting',
    description: 'Breaking down video into segments'
  },
  {
    id: 'analyzing',
    label: 'Analyzing',
    description: 'Generating insights and summaries'
  }
]; 