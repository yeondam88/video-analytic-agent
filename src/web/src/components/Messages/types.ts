export enum MessageType {
  USER = 'user',
  SYSTEM = 'system',
}

export interface Message {
  id: string;
  type: MessageType;
  content: string | string[];
  timestamp: Date;
  status?: 'success' | 'error' | 'processing';
} 