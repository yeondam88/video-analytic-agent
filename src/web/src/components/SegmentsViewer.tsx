import React, { useState, useRef, useEffect } from 'react';
import { Segment } from '../types/video';
import { logger } from '../utils/logger';

interface SegmentsViewerProps {
  videoId: string;
  segments: Segment[];
  isLoading?: boolean;
  error?: string;
  onSegmentClick?: (startTime: number) => void;
  currentTime?: number;
}

interface SearchFilters {
  minConfidence: number;
  minDuration: number;
  maxDuration: number;
  hasSummary: boolean | null;
  speakers: string[];
}

const DEFAULT_FILTERS: SearchFilters = {
  minConfidence: 0,
  minDuration: 0,
  maxDuration: Infinity,
  hasSummary: null,
  speakers: []
};

const PLAYBACK_SPEEDS = [0.5, 0.75, 1, 1.25, 1.5, 2];

export const SegmentsViewer: React.FC<SegmentsViewerProps> = ({
  videoId,
  segments,
  isLoading = false,
  error,
  onSegmentClick,
  currentTime = 0
}) => {
  logger.info(`Rendering ${segments.length} segments for video ${videoId}`);

  const [selectedSegment, setSelectedSegment] = useState<Segment | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchMode, setSearchMode] = useState<'text' | 'semantic'>('text');
  const [similarSegments, setSimilarSegments] = useState<Segment[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const timelineRef = useRef<HTMLDivElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const playbackInterval = useRef<NodeJS.Timeout>();

  // New state for features
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [showMinimap, setShowMinimap] = useState(true);
  const [minimapZoom, setMinimapZoom] = useState(1);
  const [minimapPosition, setMinimapPosition] = useState(0);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>(DEFAULT_FILTERS);
  const minimapRef = useRef<HTMLDivElement>(null);

  // Group segments by speaker
  const segmentsBySpeaker = segments.reduce((acc, segment) => {
    const speaker = segment.speaker_id || 'unknown';
    if (!acc[speaker]) {
      acc[speaker] = [];
    }
    acc[speaker].push(segment);
    return acc;
  }, {} as Record<string, Segment[]>);

  // Get unique speakers
  const uniqueSpeakers = Object.keys(segmentsBySpeaker);

  // Format time in MM:SS format
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Handle semantic search
  const handleSemanticSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const response = await fetch(`/api/videos/${videoId}/segments/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery })
      });
      const results = await response.json();
      setSimilarSegments(results);
    } catch (error) {
      console.error('Failed to perform semantic search:', error);
    } finally {
      setIsSearching(false);
    }
  };

  // Handle timeline playback with speed control
  useEffect(() => {
    if (isPlaying) {
      playbackInterval.current = setInterval(() => {
        setCurrentTime(time => {
          const newTime = time + (0.1 * playbackSpeed);
          const maxTime = segments[segments.length - 1]?.end_time || 0;
          if (newTime >= maxTime) {
            setIsPlaying(false);
            return maxTime;
          }
          return newTime;
        });
      }, 100);
    } else {
      if (playbackInterval.current) {
        clearInterval(playbackInterval.current);
      }
    }

    return () => {
      if (playbackInterval.current) {
        clearInterval(playbackInterval.current);
      }
    };
  }, [isPlaying, segments, playbackSpeed]);

  // Update selected segment based on current time
  useEffect(() => {
    const currentSegment = segments.find(
      segment => currentTime >= segment.start_time && currentTime <= segment.end_time
    );
    if (currentSegment && currentSegment.id !== selectedSegment?.id) {
      setSelectedSegment(currentSegment);
    }
  }, [currentTime, segments, selectedSegment]);

  // Apply filters to segments
  const applyFilters = (segment: Segment): boolean => {
    const metadata = segment.metadata || {};
    if (filters.minConfidence > 0 && metadata.confidence < filters.minConfidence) {
      return false;
    }
    if (metadata.duration < filters.minDuration) {
      return false;
    }
    if (filters.maxDuration < Infinity && metadata.duration > filters.maxDuration) {
      return false;
    }
    if (filters.hasSummary !== null && metadata.has_summary !== filters.hasSummary) {
      return false;
    }
    if (filters.speakers.length > 0 && !filters.speakers.includes(segment.speaker_id)) {
      return false;
    }
    return true;
  };

  // Filter segments based on search mode, query, and filters
  const filteredSegments = (searchMode === 'semantic' && similarSegments.length > 0
    ? similarSegments
    : segments.filter(segment =>
        segment.text.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (segment.display_text && segment.display_text.toLowerCase().includes(searchQuery.toLowerCase()))
      )).filter(applyFilters);

  // Handle minimap zoom and position
  const handleMinimapScroll = (e: React.WheelEvent) => {
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault();
      setMinimapZoom(z => Math.max(1, Math.min(5, z + (e.deltaY > 0 ? -0.5 : 0.5))));
    } else {
      const maxPosition = Math.max(0, (minimapZoom - 1) * 100);
      setMinimapPosition(p => Math.max(0, Math.min(maxPosition, p + e.deltaY / 10)));
    }
  };

  // Handle segment click
  const handleSegmentClick = (segment: Segment) => {
    setSelectedSegment(segment);
    if (onSegmentClick) {
      onSegmentClick(segment.start_time);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
        <p className="text-red-600">{error}</p>
      </div>
    );
  }

  if (!segments || segments.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-4">
        <p className="text-yellow-700">No segments available for this video yet. Please wait while we process the video.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Video Segments</h2>
        <span className="text-sm text-gray-500">{segments.length} segments found</span>
      </div>
      
      <div className="grid gap-4">
        {segments.map((segment) => {
          const metadata = segment.metadata || {};
          return (
            <div
              key={segment.id}
              className={`bg-white shadow-lg rounded-lg p-4 hover:shadow-xl transition-shadow cursor-pointer ${
                selectedSegment?.id === segment.id ? 'ring-2 ring-blue-500' : ''
              }`}
              onClick={() => handleSegmentClick(segment)}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-500">
                    {formatTime(segment.start_time)} - {formatTime(segment.end_time)}
                  </span>
                  {segment.speaker_id && (
                    <span className="px-2 py-1 text-xs font-medium text-blue-600 bg-blue-50 rounded-full">
                      Speaker {segment.speaker_id}
                    </span>
                  )}
                </div>
                <span className="text-xs text-gray-400">
                  {Math.round(segment.end_time - segment.start_time)}s
                </span>
              </div>
              
              <p className="text-gray-700 whitespace-pre-wrap">
                {segment.display_text || segment.text}
              </p>
              
              {metadata && Object.keys(metadata).length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-100">
                  <div className="grid grid-cols-2 gap-2 text-sm text-gray-500">
                    {Object.entries(metadata).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="font-medium capitalize">{key.replace(/_/g, ' ')}:</span>
                        <span className="text-gray-600">
                          {typeof value === 'number' ? value.toFixed(2) : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SegmentsViewer; 