import React, { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { ReloadIcon } from '@radix-ui/react-icons'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { VideoPlayer } from '@/components/VideoPlayer'
import { TranscriptViewer } from '@/components/TranscriptViewer'
import { SegmentTimeline } from '@/components/SegmentTimeline'
import { VideoSummary } from '@/components/VideoSummary'
import { VideoStatus, Segment } from '../types/video'
import { SegmentsViewer } from '../components/SegmentsViewer'
import { logger } from '../utils/logger'
import YouTube from 'react-youtube'

interface Video {
  id: string
  url: string
  title: string | null
  source_id: string
  status: VideoStatus
  progress: number
  steps_completed: string[]
  created_at: string
  error?: string
  metadata?: {
    summary?: string;
    key_points?: string[];
  }
}

interface SimilarVideo {
  id: number;  // Change to number since we're getting integer IDs from the API
  title: string | null;
  url: string;
  thumbnail_url: string | null;
  similarity_score: number;
  segment_count: number;
  avg_confidence: number;
}

interface VideoInsights {
  totalDuration: number;
  speakerCount: number;
  wordFrequency: { word: string; count: number }[];
  speakerDurations: { speaker: string; duration: number; percentage: number }[];
  summary: string | null;
  keyPoints: string[];
}

interface YouTubePlayer {
  seekTo: (seconds: number, allowSeekAhead: boolean) => void;
  playVideo: () => void;
  getPlayerState: () => number;
  getCurrentTime: () => number;
}

// Update the player state interface
interface PlayerState {
  player: YouTubePlayer | null;
  isReady: boolean;
  currentTime: number;
  isPlaying: boolean;
}

export function VideoDetailPage() {
  const { videoId } = useParams<{ videoId: string }>()
  const [playerState, setPlayerState] = useState<PlayerState>({
    player: null,
    isReady: false,
    currentTime: 0,
    isPlaying: false
  })
  const [activeSegmentId, setActiveSegmentId] = useState<string | null>(null);
  const segmentContainerRef = useRef<HTMLDivElement>(null);
  const lastSegmentClickTime = useRef<number>(0);

  const { data: video, isLoading: isVideoLoading } = useQuery<Video, Error>({
    queryKey: ['video', videoId],
    queryFn: async () => {
      const response = await fetch(`/api/videos/${videoId}`)
      if (!response.ok) {
        throw new Error('Failed to fetch video')
      }
      return response.json()
    },
    enabled: !!videoId,
    refetchInterval: (query) => {
      return query.state.data?.status === VideoStatus.COMPLETED ? false : 5000
    }
  })

  const { data: segments, isLoading: isSegmentsLoading } = useQuery<Segment[], Error>({
    queryKey: ['segments', videoId],
    queryFn: async () => {
      const response = await fetch(`/api/videos/${videoId}/segments`)
      if (!response.ok) {
        throw new Error('Failed to fetch segments')
      }
      const data = await response.json()
      logger.info(`Fetched ${data.length} segments for video ${videoId}`)
      return data
    },
    enabled: !!videoId && video?.status === VideoStatus.COMPLETED
  })

  const { data: similarVideos, isLoading: isSimilarLoading } = useQuery<SimilarVideo[], Error>({
    queryKey: ['similar-videos', videoId],
    queryFn: async () => {
      const response = await fetch(`/api/videos/${videoId}/similar`)
      if (!response.ok) {
        throw new Error('Failed to fetch similar videos')
      }
      return response.json()
    },
    enabled: !!videoId && video?.status === VideoStatus.COMPLETED
  })

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const handleTimeUpdate = (time: number) => {
    setPlayerState(prev => ({ ...prev, currentTime: time }));
    
    // Find active segment based on current time
    if (segments) {
      const activeSegment = segments.find(
        (segment) => time >= segment.start_time && time <= segment.end_time
      );
      
      if (activeSegment && activeSegment.id !== activeSegmentId) {
        setActiveSegmentId(activeSegment.id);
        const element = document.getElementById(`segment-${activeSegment.id}`);
        if (element && segmentContainerRef.current) {
          // Calculate if element is outside visible area
          const container = segmentContainerRef.current;
          const elementTop = element.offsetTop;
          const elementBottom = elementTop + element.offsetHeight;
          const containerTop = container.scrollTop;
          const containerBottom = containerTop + container.offsetHeight;

          // Only scroll if element is not fully visible
          if (elementTop < containerTop || elementBottom > containerBottom) {
            element.scrollIntoView({
              behavior: 'smooth',
              block: 'nearest'
            });
          }
        }
      }
    }
  };

  const handleSegmentClick = async (startTime: number) => {
    logger.info(`Segment clicked at ${startTime}s`);
    
    // Debounce segment clicks to prevent rapid-fire seeking
    const now = Date.now();
    if (now - lastSegmentClickTime.current < 500) {
      logger.info('Ignoring segment click - too soon after last click');
      return;
    }
    lastSegmentClickTime.current = now;

    try {
      setPlayerState(prev => ({ ...prev, currentTime: startTime }));
    } catch (error) {
      logger.error('Error handling segment click:', error);
    }
  };

  // Reset player when video changes
  useEffect(() => {
    setPlayerState(prev => ({
      ...prev,
      currentTime: 0,
      isReady: false,
      isPlaying: false
    }));
    setActiveSegmentId(null);
    lastSegmentClickTime.current = 0;
  }, [videoId]);

  const calculateInsights = (segments: Segment[], video: Video): VideoInsights => {
    // Calculate total duration
    const totalDuration = segments.reduce((total, segment) => 
      total + (segment.end_time - segment.start_time), 0);

    // Get unique speakers and their durations
    const speakerStats = segments.reduce((stats, segment) => {
      const speaker = segment.speaker_id;
      const duration = segment.end_time - segment.start_time;
      if (!stats[speaker]) {
        stats[speaker] = { duration: 0, words: 0 };
      }
      stats[speaker].duration += duration;
      stats[speaker].words += segment.text.split(' ').length;
      return stats;
    }, {} as Record<string, { duration: number; words: number }>);

    // Calculate word frequency
    const wordFreq: Record<string, number> = {};
    const stopWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']);
    
    segments.forEach(segment => {
      const words = segment.text.toLowerCase()
        .replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g, '')
        .split(/\s+/);
      
      words.forEach(word => {
        if (word.length > 3 && !stopWords.has(word)) {
          wordFreq[word] = (wordFreq[word] || 0) + 1;
        }
      });
    });

    // Sort word frequency
    const wordFrequency = Object.entries(wordFreq)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10)
      .map(([word, count]) => ({ word, count }));

    // Format speaker durations
    const speakerDurations = Object.entries(speakerStats)
      .map(([speaker, stats]) => ({
        speaker,
        duration: stats.duration,
        percentage: (stats.duration / totalDuration) * 100
      }))
      .sort((a, b) => b.duration - a.duration);

    return {
      totalDuration,
      speakerCount: Object.keys(speakerStats).length,
      wordFrequency,
      speakerDurations,
      summary: video.metadata?.summary || null,
      keyPoints: video.metadata?.key_points || []
    };
  };

  const formatDuration = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // Calculate insights when segments are available
  const insights = segments && video ? calculateInsights(segments, video) : null;

  if (isVideoLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }

  if (!video) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-600">Video not found</p>
      </div>
    )
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header with navigation */}
      <div className="flex items-center space-x-4 text-sm">
        <Link to="/" className="text-gray-500 hover:text-gray-700 flex items-center space-x-1">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span>Back to Videos</span>
        </Link>
        <span className="text-gray-300">/</span>
        <span className="text-gray-900 font-medium">Video Details</span>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Video Player and Details Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Video Player */}
          {video.status === VideoStatus.COMPLETED && video.url && (
            <div className="aspect-video bg-black rounded-xl overflow-hidden shadow-lg">
              <VideoPlayer
                url={video.url}
                currentTime={playerState.currentTime}
                onTimeUpdate={handleTimeUpdate}
                onReady={() => setPlayerState(prev => ({ ...prev, isReady: true }))}
                onStateChange={(event: { data: number }) => {
                  if (event.data === 1) {
                    setPlayerState(prev => ({ ...prev, isPlaying: true }));
                  }
                }}
                className="w-full h-full"
              />
            </div>
          )}

          {/* Video Details */}
          <div className="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-xl p-6">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <h1 className="text-2xl font-bold text-gray-900">
                  {video.title || (
                    <span className="text-gray-400">
                      {video.status === VideoStatus.COMPLETED
                        ? 'Untitled Video'
                        : 'Generating title...'}
                    </span>
                  )}
                </h1>
                <p className="text-sm text-gray-500">
                  Added {formatDate(video.created_at)}
                </p>
              </div>
              <div className="flex items-center space-x-4">
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium shadow-sm ${
                    video.status === VideoStatus.COMPLETED
                      ? 'text-green-700 bg-green-50 ring-1 ring-green-600/20'
                      : video.status === VideoStatus.FAILED
                      ? 'text-red-700 bg-red-50 ring-1 ring-red-600/20'
                      : 'text-blue-700 bg-blue-50 ring-1 ring-blue-600/20'
                  }`}
                >
                  {video.status}
                </span>
              </div>
            </div>

            {video.error && (
              <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3">
                <p className="text-sm text-red-600">{video.error}</p>
              </div>
            )}

            {video.status === VideoStatus.PROCESSING && (
              <div className="mt-4">
                <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
                    style={{ width: `${video.progress}%` }}
                  />
                </div>
                <div className="mt-2 text-sm text-gray-600">
                  {video.steps_completed.length > 0 && (
                    <p>Latest step: {video.steps_completed[video.steps_completed.length - 1]}</p>
                  )}
                </div>
              </div>
            )}

            <div className="mt-4 text-sm text-gray-600">
              <p>
                Source URL:{' '}
                <a
                  href={video.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-500 hover:underline"
                >
                  {video.url}
                </a>
              </p>
            </div>
          </div>

          {/* Segments */}
          {video.status === VideoStatus.COMPLETED && (
            <div className="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-gray-900/10">
                <h2 className="text-lg font-semibold text-gray-900">Segments</h2>
              </div>
              <div 
                ref={segmentContainerRef}
                className="divide-y divide-gray-900/10 max-h-[600px] overflow-y-auto"
              >
                {isSegmentsLoading ? (
                  <div className="p-8 text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-2 text-sm text-gray-500">Loading segments...</p>
                  </div>
                ) : segments && segments.length > 0 ? (
                  segments.map((segment) => (
                    <div
                      key={segment.id}
                      id={`segment-${segment.id}`}
                      className={`p-4 mb-2 rounded cursor-pointer transition-colors ${
                        segment.id === activeSegmentId
                          ? 'bg-blue-100 border-l-4 border-blue-500'
                          : 'bg-gray-50 hover:bg-gray-100'
                      }`}
                      onClick={() => handleSegmentClick(segment.start_time)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-500">
                          {formatDuration(segment.start_time)} - {formatDuration(segment.end_time)}
                        </span>
                        {segment.speaker_id && (
                          <span className="text-sm font-medium text-blue-600">
                            Speaker {segment.speaker_id}
                          </span>
                        )}
                      </div>
                      <p className="text-gray-800">{segment.text}</p>
                    </div>
                  ))
                ) : (
                  <div className="p-8 text-center">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 9l4-4 4 4m0 6l-4 4-4-4" />
                    </svg>
                    <p className="mt-2 text-sm text-gray-500">No segments available</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Sidebar - Insights and Similar Videos */}
        <div className="lg:col-span-1 space-y-6">
          {/* Video Insights */}
          {insights && (
            <div className="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-xl p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Video Insights</h2>
              <div className="space-y-6">
                {/* Basic Stats */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Total Duration</p>
                    <p className="text-lg font-medium text-gray-900">{formatDuration(insights.totalDuration)}</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-sm text-gray-600">Speakers</p>
                    <p className="text-lg font-medium text-gray-900">{insights.speakerCount}</p>
                  </div>
                </div>

                {/* Speaker Distribution */}
                {insights.speakerDurations.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-900 mb-3">Speaker Distribution</h3>
                    <div className="space-y-3">
                      {insights.speakerDurations.map((speaker) => (
                        <div key={speaker.speaker} className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Speaker {speaker.speaker}</span>
                            <span className="text-gray-900 font-medium">{Math.round(speaker.percentage)}%</span>
                          </div>
                          <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                            <div
                              className="bg-blue-600 h-2 rounded-full transition-width duration-500"
                              style={{ width: `${speaker.percentage}%` }}
                            />
                          </div>
                          <p className="text-xs text-gray-500">
                            {formatDuration(speaker.duration)}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Top Keywords */}
                {insights.wordFrequency.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-900 mb-3">Top Keywords</h3>
                    <div className="flex flex-wrap gap-2">
                      {insights.wordFrequency.map(({ word, count }) => (
                        <span
                          key={word}
                          className="px-2.5 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium ring-1 ring-gray-900/5"
                        >
                          {word} ({count})
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Summary */}
                {insights.summary && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-900 mb-2">Summary</h3>
                    <p className="text-sm text-gray-600 leading-relaxed">{insights.summary}</p>
                  </div>
                )}

                {/* Key Points */}
                {insights.keyPoints.length > 0 && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-gray-900 mb-2">Key Points</h3>
                    <ul className="space-y-2">
                      {insights.keyPoints.map((point, index) => (
                        <li key={index} className="flex items-start space-x-2 text-sm text-gray-600">
                          <span className="text-blue-600 mt-1">•</span>
                          <span className="flex-1">{point}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Similar Videos - Updated Design */}
          <div className="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-xl">
            <div className="p-4 border-b border-gray-900/10">
              <h2 className="text-lg font-semibold text-gray-900">Similar Videos</h2>
            </div>
            {isSimilarLoading ? (
              <div className="flex flex-col items-center py-6">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-600"></div>
                <p className="mt-2 text-sm text-gray-500">Loading similar videos...</p>
              </div>
            ) : similarVideos && similarVideos.length > 0 ? (
              <div className="divide-y divide-gray-900/5">
                {similarVideos.map((video) => (
                  <Link
                    key={video.id}
                    to={`/videos/${video.id}`}
                    className="block hover:bg-gray-50 transition-colors duration-150 group"
                  >
                    <div className="p-3 flex items-start space-x-3">
                      {video.thumbnail_url ? (
                        <img
                          src={video.thumbnail_url}
                          alt={video.title || 'Video thumbnail'}
                          className="w-20 h-14 object-cover rounded-md shadow-sm ring-1 ring-gray-900/5 group-hover:ring-blue-500/20"
                        />
                      ) : (
                        <div className="w-20 h-14 bg-gray-100 rounded-md flex items-center justify-center group-hover:bg-gray-200 transition-colors">
                          <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-medium text-gray-900 truncate group-hover:text-blue-600">
                          {video.title || 'Untitled Video'}
                        </h3>
                        <div className="flex items-center mt-1 space-x-1.5">
                          <span className="inline-flex items-center px-1.5 py-0.5 rounded-md text-xs font-medium bg-gray-100 text-gray-700">
                            {video.segment_count} segments
                          </span>
                          <span className="inline-flex items-center px-1.5 py-0.5 rounded-md text-xs font-medium bg-blue-50 text-blue-700">
                            {Math.ceil(video.similarity_score * 100)}% match
                          </span>
                        </div>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="py-6 text-center">
                <svg className="mx-auto h-10 w-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                <p className="mt-2 text-sm text-gray-500">No similar videos found</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}