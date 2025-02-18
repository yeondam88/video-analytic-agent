import React from 'react';
import { Progress } from './ui/progress';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { VideoStatus } from '../types/video';

interface ProcessingStep {
  step: string;
  timestamp: string;
  status: string;
  progress: number;
  error?: string;
}

interface VideoProgressProps {
  status: string;
  progress: number;
  processingDetails?: ProcessingStep[];
}

const stepLabels: Record<string, string> = {
  'download_started': 'Starting download',
  'download_completed': 'Download completed',
  'audio_extraction_started': 'Extracting audio',
  'audio_extraction_completed': 'Audio extracted',
  'transcription_started': 'Transcribing video',
  'transcription_completed': 'Transcription completed',
  'segmentation_started': 'Processing segments',
  'segmentation_completed': 'Segmentation completed',
  'processing_completed': 'Processing completed',
  'processing_failed': 'Processing failed'
};

export const VideoProgress: React.FC<VideoProgressProps> = ({
  status,
  progress,
  processingDetails = []
}) => {
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'text-green-500';
      case 'FAILED':
        return 'text-red-500';
      case 'PROCESSING':
        return 'text-blue-500';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Processing Status</span>
          <span className={getStatusColor(status)}>{status}</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <Progress value={progress} className="h-2" />
          <p className="text-sm text-gray-500 mt-1">{progress.toFixed(1)}% complete</p>
        </div>
        
        {processingDetails.length > 0 && (
          <div className="space-y-2">
            <h3 className="text-sm font-medium">Processing Steps:</h3>
            <div className="space-y-1">
              {processingDetails.map((step, index) => (
                <div 
                  key={index} 
                  className="text-sm flex items-center justify-between py-1 border-b border-gray-100"
                >
                  <span>{stepLabels[step.step] || step.step}</span>
                  <div className="flex items-center space-x-2">
                    <span className={getStatusColor(step.status)}>
                      {step.progress.toFixed(1)}%
                    </span>
                    <span className="text-gray-400 text-xs">
                      {formatTimestamp(step.timestamp)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {status === 'FAILED' && (
          <div className="mt-4 p-2 bg-red-50 text-red-700 rounded">
            {processingDetails[processingDetails.length - 1]?.error || 'Processing failed'}
          </div>
        )}
      </CardContent>
    </Card>
  );
}; 