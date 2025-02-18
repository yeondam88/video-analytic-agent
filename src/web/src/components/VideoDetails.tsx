import React from 'react';
import { VideoProgress } from './VideoProgress';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Video } from '../types/video';

interface VideoDetailsProps {
  video: Video;
}

export const VideoDetails: React.FC<VideoDetailsProps> = ({ video }) => {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>{video.title || 'Untitled Video'}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p className="text-sm text-gray-500">Source: {video.source}</p>
            <p className="text-sm text-gray-500">URL: {video.url}</p>
            {video.description && (
              <p className="text-sm text-gray-700">{video.description}</p>
            )}
          </div>
        </CardContent>
      </Card>

      <VideoProgress 
        status={video.status}
        progress={video.progress}
        processingDetails={video.processing_details}
      />
    </div>
  );
}; 