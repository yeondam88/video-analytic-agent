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
  LOCAL = "LOCAL",
  OTHER = "OTHER"
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
  description: string | null;
  status: VideoStatus;
  progress: number;
  steps_completed?: string[];
  created_at: string;
  error?: string;
  thumbnail_url?: string;
  source?: VideoSource;
  duration?: number;
  extra_data?: Record<string, any>;
  metadata?: {
    summary?: string;
    key_points?: string[];
    tags?: string[];
    category?: string;
    duration?: number;
    thumbnail_url?: string;
    speakers?: {
      id: string;
      name?: string;
      duration: number;
      word_count: number;
      confidence?: number;
    }[];
    word_frequency?: {
      word: string;
      count: number;
    }[];
    sentiment?: {
      overall: number;
      segments: {
        start_time: number;
        end_time: number;
        score: number;
      }[];
    };
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

export interface VideoSegment {
  id: string;
  video_id: string;
  text: string;
  start_time: number;
  end_time: number;
  speaker_id?: string;
  created_at: string;
  embedding?: number[];
}

export interface Segment {
  id: string;
  video_id: string;
  speaker_id: string;
  start_time: number;
  end_time: number;
  text: string;
  display_text?: string;
  metadata?: {
    word_count?: number;
    duration?: number;
    has_summary?: boolean;
    confidence?: number;
  };
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