import React, { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { VideoStatus, VideoSource } from '../types/video'
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
import { VideoGrid } from '@/components/VideoGrid';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface FilterOptions {
  source?: VideoSource;
  category?: string;
  tag?: string;
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
  const [activeTab, setActiveTab] = useState<string>("all")
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

  const getSourceIcon = (source: VideoSource) => {
    switch (source) {
      case VideoSource.YOUTUBE:
        return <Youtube className="w-5 h-5 text-red-600" />;
      case VideoSource.LOOM:
        return <VideoIcon className="w-5 h-5 text-purple-600" />;
      default:
        return <VideoIcon className="w-5 h-5 text-gray-600" />;
    }
  };

  const getSourceTitle = (source: VideoSource): string => {
    switch (source) {
      case VideoSource.YOUTUBE:
        return 'YouTube Videos';
      case VideoSource.LOOM:
        return 'Loom Recordings';
      default:
        return 'Other Videos';
    }
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  const getStatusColor = (status: VideoStatus) => {
    switch (status) {
      case VideoStatus.COMPLETED:
        return 'text-green-600 bg-green-50'
      case VideoStatus.FAILED:
        return 'text-red-600 bg-red-50'
      case VideoStatus.PROCESSING:
        return 'text-blue-600 bg-blue-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  const handleCardClick = (video: Video) => {
    navigate(`/videos/${video.id}`)
  }

  const handleAddVideo = () => {
    setIsAddVideoModalOpen(true);
  };

  const processedVideos = videos?.map(video => ({
    ...video,
    duration: video.metadata?.duration || 0,
    thumbnail_url: video.metadata?.thumbnail_url || null,
  })) || [];

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold">Your Videos</h1>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <Filter className="w-4 h-4 mr-2" />
              Filters
            </button>
            <AddVideoButton onClick={handleAddVideo} />
          </div>
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
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold">Your Videos</h1>
        <div className="flex items-center space-x-4">
          <div className="flex gap-4">
            <Input
              type="text"
              placeholder="Search videos..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-96"
            />
            <Select value={selectedSource} onValueChange={setSelectedSource}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="All Sources" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">All Sources</SelectItem>
                <SelectItem value="YOUTUBE">YouTube</SelectItem>
                <SelectItem value="LOOM">Loom</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button
            variant="outline"
            size="icon"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="h-4 w-4" />
          </Button>
          <AddVideoButton onClick={handleAddVideo} />
        </div>
      </div>

      {showFilters && (
        <div className="bg-white rounded-lg shadow-sm mb-8 p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-4">Filters</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Source filter has been moved to the search box */}
          </div>
        </div>
      )}

      <Tabs defaultValue={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 lg:w-[400px]">
          <TabsTrigger value="all">
            All
          </TabsTrigger>
          <TabsTrigger value="youtube">
            <Youtube className="w-4 h-4 mr-2" />
            YouTube
          </TabsTrigger>
          <TabsTrigger value="loom">
            <VideoIcon className="w-4 h-4 mr-2" />
            Loom
          </TabsTrigger>
          <TabsTrigger value="other">
            Other
          </TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-8">
          {/* Processing Videos */}
          {displayedVideos.processing.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold">Processing</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {displayedVideos.processing.map(video => (
                  <VideoProcessingSkeleton key={video.id} />
                ))}
              </div>
            </div>
          )}

          {/* All Completed Videos */}
          {Object.entries(displayedVideos.completed).map(([source, sourceVideos]) => (
            <div key={source} className="space-y-4">
              <div className="flex items-center space-x-2">
                {getSourceIcon(source as VideoSource)}
                <h2 className="text-xl font-semibold">{getSourceTitle(source as VideoSource)}</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {sourceVideos.map(video => (
                  <Link
                    key={video.id}
                    to={`/videos/${video.id}`}
                    className="block group"
                  >
                    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow min-h-[400px] flex flex-col">
                      <div className="aspect-video bg-gray-100 relative">
                        {video.thumbnail_url ? (
                          <img
                            src={video.thumbnail_url}
                            alt={video.title || 'Video thumbnail'}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="absolute inset-0 flex items-center justify-center">
                            <span className="text-gray-400">
                              {video.status === VideoStatus.FAILED ? (
                                <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                              ) : (
                                <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                </svg>
                              )}
                            </span>
                          </div>
                        )}
                      </div>
                      <div className="p-4 flex-1 flex flex-col">
                        <div className="flex justify-between items-start">
                          <div className="space-y-1">
                            <h3 className="text-lg font-semibold text-gray-900">
                              {video.title || 'Untitled Video'}
                            </h3>
                            <p className="text-sm text-gray-500">
                              Added {formatDate(video.created_at)}
                            </p>
                          </div>
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(video.status)}`}
                          >
                            {video.status}
                          </span>
                        </div>
                        {video.description && (
                          <p className="text-sm text-gray-600 line-clamp-2 mt-2">
                            {video.description}
                          </p>
                        )}
                        {video.metadata?.summary && (
                          <p className="text-sm text-gray-600 line-clamp-2 mt-2">
                            {video.metadata.summary}
                          </p>
                        )}
                        {video.error && (
                          <p className="text-sm text-red-600 mt-2">
                            {video.error}
                          </p>
                        )}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </TabsContent>

        <TabsContent value="youtube" className="space-y-8">
          {Object.values(displayedVideos.completed)
            .flat()
            .filter((video) => getVideoSource(video) === "YOUTUBE")
            .map((video) => (
              <Link
                key={video.id}
                to={`/videos/${video.id}`}
                className="block group"
              >
                <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow min-h-[400px] flex flex-col">
                  <div className="aspect-video bg-gray-100 relative">
                    {video.thumbnail_url ? (
                      <img
                        src={video.thumbnail_url}
                        alt={video.title || 'Video thumbnail'}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-gray-400">
                          {video.status === VideoStatus.FAILED ? (
                            <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          ) : (
                            <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                          )}
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="p-4 flex-1 flex flex-col">
                    <div className="flex justify-between items-start">
                      <div className="space-y-1">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {video.title || 'Untitled Video'}
                        </h3>
                        <p className="text-sm text-gray-500">
                          Added {formatDate(video.created_at)}
                        </p>
                      </div>
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(video.status)}`}
                      >
                        {video.status}
                      </span>
                    </div>
                    {video.description && (
                      <p className="text-sm text-gray-600 line-clamp-2 mt-2">
                        {video.description}
                      </p>
                    )}
                    {video.metadata?.summary && (
                      <p className="text-sm text-gray-600 line-clamp-2 mt-2">
                        {video.metadata.summary}
                      </p>
                    )}
                    {video.error && (
                      <p className="text-sm text-red-600 mt-2">
                        {video.error}
                      </p>
                    )}
                  </div>
                </div>
              </Link>
            ))}
        </TabsContent>

        <TabsContent value="loom" className="space-y-8">
          {Object.values(displayedVideos.completed)
            .flat()
            .filter((video) => getVideoSource(video) === "LOOM")
            .map((video) => (
              <Link
                key={video.id}
                to={`/videos/${video.id}`}
                className="block group"
              >
                <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow min-h-[400px] flex flex-col">
                  <div className="aspect-video bg-gray-100 relative">
                    {video.thumbnail_url ? (
                      <img
                        src={video.thumbnail_url}
                        alt={video.title || 'Video thumbnail'}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-gray-400">
                          {video.status === VideoStatus.FAILED ? (
                            <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          ) : (
                            <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                          )}
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="p-4 flex-1 flex flex-col">
                    <div className="flex justify-between items-start">
                      <div className="space-y-1">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {video.title || 'Untitled Video'}
                        </h3>
                        <p className="text-sm text-gray-500">
                          Added {formatDate(video.created_at)}
                        </p>
                      </div>
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(video.status)}`}
                      >
                        {video.status}
                      </span>
                    </div>
                    {video.description && (
                      <p className="text-sm text-gray-600 line-clamp-2 mt-2">
                        {video.description}
                      </p>
                    )}
                    {video.metadata?.summary && (
                      <p className="text-sm text-gray-600 line-clamp-2 mt-2">
                        {video.metadata.summary}
                      </p>
                    )}
                    {video.error && (
                      <p className="text-sm text-red-600 mt-2">
                        {video.error}
                      </p>
                    )}
                  </div>
                </div>
              </Link>
            ))}
        </TabsContent>

        <TabsContent value="other" className="space-y-8">
          {Object.values(displayedVideos.completed)
            .flat()
            .filter((video) => getVideoSource(video) === "OTHER")
            .map((video) => (
              <Link
                key={video.id}
                to={`/videos/${video.id}`}
                className="block group"
              >
                <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow min-h-[400px] flex flex-col">
                  <div className="aspect-video bg-gray-100 relative">
                    {video.thumbnail_url ? (
                      <img
                        src={video.thumbnail_url}
                        alt={video.title || 'Video thumbnail'}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-gray-400">
                          {video.status === VideoStatus.FAILED ? (
                            <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                          ) : (
                            <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                          )}
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="p-4 flex-1 flex flex-col">
                    <div className="flex justify-between items-start">
                      <div className="space-y-1">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {video.title || 'Untitled Video'}
                        </h3>
                        <p className="text-sm text-gray-500">
                          Added {formatDate(video.created_at)}
                        </p>
                      </div>
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(video.status)}`}
                      >
                        {video.status}
                      </span>
                    </div>
                    {video.description && (
                      <p className="text-sm text-gray-600 line-clamp-2 mt-2">
                        {video.description}
                      </p>
                    )}
                    {video.metadata?.summary && (
                      <p className="text-sm text-gray-600 line-clamp-2 mt-2">
                        {video.metadata.summary}
                      </p>
                    )}
                    {video.error && (
                      <p className="text-sm text-red-600 mt-2">
                        {video.error}
                      </p>
                    )}
                  </div>
                </div>
              </Link>
            ))}
        </TabsContent>
      </Tabs>

      {isAddVideoModalOpen && (
        <AddVideoModal onClose={() => setIsAddVideoModalOpen(false)} />
      )}
    </div>
  )
} 