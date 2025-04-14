import React, { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { VideoStatus, VideoSource, Segment } from '../types/video'
import { logger } from '../utils/logger'
import { Trash2, Youtube, Video as VideoIcon, Filter } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { VideoPlayer } from '../components/VideoPlayer'
import { AddVideoModal } from '../components/AddVideoModal'
import { VideoProgressModal } from '../components/VideoProgressModal'
import { VideoProcessingSkeleton } from '../components/VideoProcessingSkeleton'
import { AddVideoButton } from '../components/AddVideoButton'
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useDebounce } from "@/hooks/useDebounce";
import { useSearch } from "@/hooks/useSearch";
import { Spinner } from "@/components/ui/spinner";
import { Video } from "@/types/video";
import { VideoGrid } from '../components/VideoGrid';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ChatUI } from '../components/ChatUI';
import { ThinkingComponent } from '@/components/ThinkingComponent/ThinkingComponent'

interface FilterOptions {
  source?: VideoSource;
  category?: string;
  tag?: string;
}

interface GridVideo {
  id: string;
  title: string;
  thumbnail_url: string;
  duration: number;
  status: string;
  progress: number;
  source: VideoSource;
  created_at: string;
  error?: string;
}

export function HomePage() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null)
  const [showProgress, setShowProgress] = useState<Video | null>(null)
  const [currentTime, setCurrentTime] = useState(0)
  const [isAddVideoModalOpen, setIsAddVideoModalOpen] = useState(false)
  const [filterOptions, setFilterOptions] = useState<FilterOptions>({})
  const [showFilters, setShowFilters] = useState(false)
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSource, setSelectedSource] = useState<string>("ALL");
  const debouncedQuery = useDebounce(searchQuery, 300);

  const getVideoSource = (video: Video): VideoSource => {
    const url = video.url.toLowerCase();
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
      return VideoSource.YOUTUBE;
    }
    if (url.includes('loom.com')) {
      return VideoSource.LOOM;
    }
    return VideoSource.OTHER;
  };

  const { data: videos, isLoading, error } = useQuery<Video[]>({
    queryKey: ['videos'],
    queryFn: async () => {
      const response = await fetch('/api/videos')
      if (!response.ok) {
        throw new Error('Failed to fetch videos')
      }
      const data = await response.json()
      logger.info(`Fetched ${data.length} videos`)
      logger.info(data)
      return data
    },
    refetchInterval: (query) => {
      const data = query.state.data as Video[] | undefined
      if (!data) return false
      const hasProcessingVideos = data.some(
        video => video.status !== VideoStatus.COMPLETED && 
                video.status !== VideoStatus.FAILED
      )
      return hasProcessingVideos ? 5000 : false
    }
  })

  const { data: searchResults, isLoading: isSearching } = useSearch(debouncedQuery, {
    source: selectedSource === "ALL" ? undefined : [selectedSource],
    enabled: debouncedQuery.length > 0,
  });

  const displayedVideos = useMemo(() => {
    if (debouncedQuery && searchResults) {
      return {
        processing: [],
        completed: {
          [VideoSource.YOUTUBE]: searchResults.results.filter(
            (video) => getVideoSource(video) === VideoSource.YOUTUBE
          ),
          [VideoSource.LOOM]: searchResults.results.filter(
            (video) => getVideoSource(video) === VideoSource.LOOM
          ),
          [VideoSource.OTHER]: searchResults.results.filter(
            (video) => getVideoSource(video) === VideoSource.OTHER
          ),
        },
      };
    }
    
    if (!videos) return { processing: [], completed: {} as Record<VideoSource, Video[]> };

    const processing = videos.filter(
      (video) => video.status !== VideoStatus.COMPLETED && video.status !== VideoStatus.FAILED
    );

    const completed = videos
      .filter((video) => video.status === VideoStatus.COMPLETED)
      .reduce((acc, video) => {
        const source = getVideoSource(video);
        if (!acc[source]) {
          acc[source] = [];
        }
        acc[source].push(video);
        return acc;
      }, {} as Record<VideoSource, Video[]>);

    return { processing, completed };
  }, [videos, debouncedQuery, searchResults]);

  const deleteMutation = useMutation({
    mutationFn: async (videoId: string) => {
      const response = await fetch(`/api/videos/${videoId}`, {
        method: 'DELETE',
      })
      if (!response.ok) {
        throw new Error('Failed to delete video')
      }
      return videoId
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['videos'] })
    },
  })

  const handleDelete = async (videoId: string, event: React.MouseEvent) => {
    event.preventDefault()
    if (window.confirm('Are you sure you want to delete this video?')) {
      try {
        await deleteMutation.mutateAsync(videoId)
      } catch (error) {
        logger.error(`Failed to delete video ${videoId}:`, error)
      }
    }
  }

  const handleAddVideo = () => {
    setIsAddVideoModalOpen(true);
  };

  // Transform videos to match GridVideo format
  const gridVideos: GridVideo[] = videos?.map(video => ({
    id: video.id,
    title: video.title || 'Untitled Video',
    thumbnail_url: video.thumbnail_url || video.metadata?.thumbnail_url || '',
    duration: video.metadata?.duration || 0,
    status: video.status,
    progress: video.progress,
    source: video.source || VideoSource.OTHER,
    created_at: video.created_at,
    error: video.error
  })) || [];

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold">Your Videos</h1>
          
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <VideoProcessingSkeleton />
          <VideoProcessingSkeleton />
          <VideoProcessingSkeleton />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-600">Error loading videos: {error.message}</p>
      </div>
    )
  }

  if (!displayedVideos || (!displayedVideos.processing.length && Object.keys(displayedVideos.completed).length === 0)) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold">Your Videos</h1>
          <AddVideoButton onClick={handleAddVideo} />
        </div>
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No videos yet
          </h3>
          <p className="text-gray-500">
            Click the "Add Video" button to get started
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="space-y-8">
        {/* Recent Videos */}
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </button>
          <AddVideoButton onClick={handleAddVideo} />
          <ChatUI 
            onSegmentClick={(videoId, timestamp) => {
              navigate(`/videos/${videoId}?t=${timestamp}`);
            }}
            onSearch={setSearchQuery}
          />
        </div>
        <div className="bg-white shadow-sm ring-1 ring-gray-900/5 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">Recent Videos</h2>
          <VideoGrid 
            videos={gridVideos} 
            isLoading={isLoading} 
            onDeleteVideo={(videoId) => handleDelete(videoId, new Event('click') as any)}
          />
        </div>
      </div>

      {/* Add Video Modal */}
      {isAddVideoModalOpen && (
        <AddVideoModal 
          onClose={() => setIsAddVideoModalOpen(false)}
        />
      )}

      {/* Video Progress Modal */}
      {showProgress && (
        <VideoProgressModal
          video={showProgress}
          onClose={() => setShowProgress(null)}
        />
      )}
    </div>
  )
} 