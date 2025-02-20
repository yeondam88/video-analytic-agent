import React, { useState, useEffect, useRef } from 'react'
import { useParams, Link, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { ReloadIcon } from '@radix-ui/react-icons'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { VideoPlayer } from '@/components/VideoPlayer'
import { TranscriptViewer } from '@/components/TranscriptViewer'
import { SegmentTimeline } from '@/components/SegmentTimeline'
import { VideoSummary } from '@/components/VideoSummary'
import { VideoStatus, Segment, Video } from '../types/video'
import { SegmentsViewer } from '../components/SegmentsViewer'
import { VideoDetails } from '../components/VideoDetails'
import { AuroraBackground } from '../components/AuroraBackground'
import { logger } from '../utils/logger'
import YouTube from 'react-youtube'

interface SimilarVideo {
  id: number;
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
  pauseVideo: () => void;
  getPlayerState: () => number;
  getCurrentTime: () => number;
}

interface PlayerState {
  player: YouTubePlayer | null;
  isReady: boolean;
  currentTime: number;
  isPlaying: boolean;
}

interface VideoDetailPageProps {}

export function VideoDetailPage() {
  const { videoId } = useParams<{ videoId: string }>()
  const [searchParams] = useSearchParams();
  const startTime = searchParams.get('start') ? parseFloat(searchParams.get('start')!) : 0;
  const endTime = searchParams.get('end') ? parseFloat(searchParams.get('end')!) : undefined;
  
  // Log the timestamp parameters
  useEffect(() => {
    if (startTime > 0 || endTime) {
      logger.info(`Initializing video with timestamps - Start: ${startTime}s, End: ${endTime}s`);
    }
  }, [startTime, endTime]);

  const [playerState, setPlayerState] = useState<PlayerState>({
    player: null,
    isReady: false,
    currentTime: startTime, // Initialize with startTime from URL
    isPlaying: false
  });

  // Add a flag to track if initial seek has been performed
  const hasPerformedInitialSeek = useRef(false);

  // Update the useEffect for initial seeking to handle the flag
  useEffect(() => {
    if (playerState.player && playerState.isReady && startTime > 0 && !hasPerformedInitialSeek.current) {
      logger.info(`Performing initial seek to ${startTime}s`);
      playerState.player.seekTo(startTime, true);
      hasPerformedInitialSeek.current = true;
      // Auto-play after seeking
      playerState.player.playVideo();
      setPlayerState(prev => ({ ...prev, isPlaying: true }));
    }
  }, [playerState.player, playerState.isReady, startTime]);

  // Reset the initial seek flag when video changes
  useEffect(() => {
    hasPerformedInitialSeek.current = false;
    setPlayerState(prev => ({
      ...prev,
      currentTime: startTime, // Update to use startTime instead of 0
      isReady: false,
      isPlaying: false
    }));
    setActiveSegmentId(null);
    lastSegmentClickTime.current = 0;
  }, [videoId, startTime]);

  // Update handleTimeUpdate to handle end time more reliably
  const handleTimeUpdate = (time: number) => {
    setPlayerState(prev => ({ ...prev, currentTime: time }));
    
    // Check if we've reached the end time
    if (endTime && time >= endTime && playerState.player) {
      try {
        logger.info(`Reached end time (${endTime}s), pausing video`);
        playerState.player.pauseVideo();
        setPlayerState(prev => ({ ...prev, isPlaying: false }));
      } catch (error) {
        logger.error('Error pausing video:', error);
      }
    }
    
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

  const [activeSegmentId, setActiveSegmentId] = useState<string | null>(null);
  const segmentContainerRef = useRef<HTMLDivElement>(null);
  const lastSegmentClickTime = useRef<number>(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<Segment[]>([]);
  const [isSearching, setIsSearching] = useState(false);

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

  // Add search function
  const handleSearch = async (query: string) => {
    if (!query.trim() || !videoId) return;
    
    setIsSearching(true);
    try {
      const response = await fetch(`/api/search/segments/${videoId}?query=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error('Search failed');
      const results = await response.json();
      setSearchResults(results);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setIsSearching(false);
    }
  };

  // Add debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery) handleSearch(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Add render function for segments
  const renderSegments = () => {
    if (isSegmentsLoading) {
      return <div>Loading segments...</div>;
    }

    if (!segments || segments.length === 0) {
      return <div>No segments available</div>;
    }

    return (
      <SegmentsViewer
        videoId={videoId!}
        segments={segments}
        isLoading={isSegmentsLoading}
        currentTime={playerState.currentTime}
        onSegmentClick={handleTimeUpdate}
      />
    );
  };

  if (isVideoLoading) {
    return (
      <AuroraBackground>
        <div className="flex justify-center items-center min-h-screen">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      </AuroraBackground>
    );
  }

  if (!video) {
    return (
      <AuroraBackground>
        <div className="flex justify-center items-center min-h-screen">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-600">Video not found</p>
          </div>
        </div>
      </AuroraBackground>
    );
  }

  return (
    <AuroraBackground>
      <div className="min-h-screen">
        <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
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
                    onReady={() => {
                      logger.info('Video player ready');
                      setPlayerState(prev => ({ ...prev, isReady: true }));
                    }}
                    onStateChange={(event: { data: number }) => {
                      logger.info(`Video player state changed: ${event.data}`);
                      setPlayerState(prev => ({ ...prev, isPlaying: event.data === 1 }));
                    }}
                    className="w-full h-full"
                  />
                </div>
              )}

              {/* Video Details */}
              <VideoDetails video={video} />

              {/* Segments */}
              {video.status === VideoStatus.COMPLETED && (
                <div className="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-xl overflow-hidden">
                  <div className="p-4 border-b border-gray-900/10">
                    <div className="flex items-center justify-between">
                      <h2 className="text-lg font-semibold">Segments</h2>
                      <div className="relative w-64">
                        <input
                          type="text"
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          placeholder="Search segments..."
                          className="w-full px-3 py-2 border rounded-md"
                        />
                        {isSearching && (
                          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                            <div className="animate-spin h-4 w-4 border-2 border-blue-500 rounded-full border-t-transparent"></div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  <div 
                    ref={segmentContainerRef}
                    className="divide-y divide-gray-900/10 max-h-[600px] overflow-y-auto"
                  >
                    {renderSegments()}
                  </div>
                </div>
              )}
            </div>

            {/* Right Sidebar - Insights and Similar Videos */}
            <div className="lg:col-span-1 space-y-6">
              {/* Similar Videos */}
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
                    {similarVideos.map((similarVideo) => (
                      <Link
                        key={similarVideo.id}
                        to={`/videos/${similarVideo.id}`}
                        className="block hover:bg-gray-50 transition-colors duration-150 group"
                      >
                        <div className="p-3 flex items-start space-x-3">
                          {similarVideo.thumbnail_url ? (
                            <img
                              src={similarVideo.thumbnail_url}
                              alt={similarVideo.title || 'Video thumbnail'}
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
                              {similarVideo.title || 'Untitled Video'}
                            </h3>
                            <div className="flex items-center mt-1 space-x-1.5">
                              <span className="inline-flex items-center px-1.5 py-0.5 rounded-md text-xs font-medium bg-gray-100 text-gray-700">
                                {similarVideo.segment_count} segments
                              </span>
                              <span className="inline-flex items-center px-1.5 py-0.5 rounded-md text-xs font-medium bg-blue-50 text-blue-700">
                                {Math.ceil(similarVideo.similarity_score * 100)}% match
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
            </div>
          </div>
        </div>
      </div>
    </AuroraBackground>
  );
}