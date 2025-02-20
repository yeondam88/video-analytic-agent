import React from 'react';
import { VideoProgress } from './VideoProgress';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Video, VideoSource } from '../types/video';
import { formatNumber, formatDate } from '../utils/format';

interface VideoDetailsProps {
  video: Video;
}

export const VideoDetails: React.FC<VideoDetailsProps> = ({ video }) => {
  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      {/* Main Video Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-start justify-between">
            <span>{video.title || 'Untitled Video'}</span>
            {video.source === VideoSource.YOUTUBE && video.extra_data?.view_count && (
              <span className="text-sm font-normal text-gray-500">
                {formatNumber(video.extra_data.view_count)} views
              </span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Video Stats */}
            <div className="flex flex-wrap gap-4 text-sm text-gray-500">
              {video.duration && (
                <span className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {formatDuration(video.duration)}
                </span>
              )}
              {video.source && (
                <span className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                  {video.source}
                </span>
              )}
              {video.created_at && (
                <span className="flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  {formatDate(video.created_at)}
                </span>
              )}
            </div>

            {/* Description */}
            {video.description && (
              <div className="mt-4">
                <h3 className="text-sm font-medium text-gray-900 mb-2">Description</h3>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{video.description}</p>
              </div>
            )}

            {/* YouTube Stats */}
            {video.source === VideoSource.YOUTUBE && video.extra_data && (
              <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                {video.extra_data.uploader && (
                  <div className="text-sm">
                    <p className="text-gray-500">Channel</p>
                    <p className="font-medium">{video.extra_data.uploader}</p>
                  </div>
                )}
                {video.extra_data.like_count && (
                  <div className="text-sm">
                    <p className="text-gray-500">Likes</p>
                    <p className="font-medium">{formatNumber(video.extra_data.like_count)}</p>
                  </div>
                )}
                {video.extra_data.upload_date && (
                  <div className="text-sm">
                    <p className="text-gray-500">Upload Date</p>
                    <p className="font-medium">
                      {new Date(video.extra_data.upload_date.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3')).toLocaleDateString()}
                    </p>
                  </div>
                )}
                {video.extra_data.format && (
                  <div className="text-sm">
                    <p className="text-gray-500">Quality</p>
                    <p className="font-medium">{video.extra_data.format.split(' - ')[1]}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Processing Status */}
      <VideoProgress 
        status={video.status}
        progress={video.progress}
      />
    </div>
  );
}; 