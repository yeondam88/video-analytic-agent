import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { VideoStatus } from '../types/video';
import { ProcessingStatus } from '../components/ProcessingStatus';
import { SegmentsViewer } from '../components/SegmentsViewer';
import { VideoUploader } from '../components/VideoUploader';
import { logger } from '../utils/logger';

interface VideoData {
  id: string;
  status: VideoStatus;
  progress: number;
  steps_completed: string[];
  error?: string;
}

const VideoProcessingPage: React.FC = () => {
  const [videoId, setVideoId] = useState<string | null>(null);

  // Mutation for video upload/URL submission
  const uploadMutation = useMutation({
    mutationFn: async (url: string) => {
      const response = await fetch('/api/videos/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      if (!response.ok) {
        throw new Error('Failed to process video');
      }
      const data = await response.json();
      return data;
    },
    onSuccess: (data) => {
      setVideoId(data.id);
    }
  });

  // Query for video processing status
  const { data: videoData, isLoading: isLoadingVideo } = useQuery<VideoData>({
    queryKey: ['video', videoId],
    queryFn: async () => {
      if (!videoId) return null;
      const response = await fetch(`/api/videos/${videoId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch video status');
      }
      return response.json();
    },
    enabled: !!videoId,
    refetchInterval: (data) => {
      // Refetch every 2 seconds until processing is complete
      return data?.status === VideoStatus.COMPLETED ? false : 2000;
    }
  });

  // Query for video segments
  const { data: segments, isLoading: isLoadingSegments } = useQuery({
    queryKey: ['segments', videoId],
    queryFn: async () => {
      if (!videoId) return [];
      const response = await fetch(`/api/videos/${videoId}/segments`);
      if (!response.ok) {
        throw new Error('Failed to fetch segments');
      }
      const data = await response.json();
      logger.info(`Fetched ${data.length} segments for video ${videoId}`);
      return data;
    },
    enabled: !!videoId && videoData?.status === VideoStatus.COMPLETED,
    refetchInterval: false  // Don't auto-refetch once we have the segments
  });

  const handleUpload = (url: string) => {
    uploadMutation.mutate(url);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Video Processing</h1>
      
      {/* Video Upload Section */}
      {!videoId && (
        <div className="mb-8">
          <VideoUploader 
            onUpload={handleUpload} 
            isLoading={uploadMutation.isLoading} 
          />
        </div>
      )}

      {/* Processing Status */}
      {videoId && videoData && videoData.status !== VideoStatus.COMPLETED && (
        <div className="mb-8">
          <ProcessingStatus
            status={videoData.status}
            progress={videoData.progress}
            steps={videoData.steps_completed}
          />
        </div>
      )}

      {/* Segments Viewer */}
      {videoId && videoData?.status === VideoStatus.COMPLETED && segments && !isLoadingSegments && (
        <div className="mt-8">
          <SegmentsViewer
            videoId={videoId}
            segments={segments}
          />
        </div>
      )}

      {/* Loading States */}
      {(isLoadingVideo || isLoadingSegments) && (
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
        </div>
      )}

      {/* Error Display */}
      {(uploadMutation.error || videoData?.error) && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mt-4">
          {String(uploadMutation.error || videoData?.error)}
        </div>
      )}
    </div>
  );
};

export default VideoProcessingPage; 