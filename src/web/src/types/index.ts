export type VideoStatus = 
  | 'pending'
  | 'downloading'
  | 'downloaded'
  | 'extracting_audio'
  | 'transcribing'
  | 'segmenting'
  | 'completed'
  | 'failed';

export interface Video {
  id: string;
  title: string;
  description: string;
  url: string;
  thumbnail_url: string | null;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
}

export interface Segment {
  id: string;
  video_id: string;
  start_time: number;
  end_time: number;
  text: string;
  display_text?: string;
  title?: string;
  speaker_id: string;
  confidence: number;
  created_at: string;
  updated_at: string;
}

export interface Transcription {
  id: string;
  video_id: string;
  text: string;
  language: string;
  created_at: string;
  updated_at: string;
}

export interface Speaker {
  id: string;
  name: string;
  segments: Segment[];
} 