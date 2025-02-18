import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { VideoStatus } from '../types/video'
import { logger } from '../utils/logger'
import { Trash2 } from 'lucide-react'
import { VideoPlayer } from '../components/VideoPlayer'
import { AddVideoModal } from '../components/AddVideoModal'
import { VideoProgressModal } from '../components/VideoProgressModal'
import { VideoProcessingSkeleton } from '../components/VideoProcessingSkeleton'
import { AddVideoButton } from '../components/AddVideoButton'

interface Video {
  id: string
  url: string
  title: string | null
  description: string | null
  status: VideoStatus
  progress: number
  steps_completed?: string[]
  created_at: string
  error?: string
  thumbnail_url?: string
  metadata?: {
    summary?: string;
    key_points?: string[];
  }
}

export function HomePage() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null)
  const [showProgress, setShowProgress] = useState<Video | null>(null)
  const [currentTime, setCurrentTime] = useState(0)
  const [showAddVideo, setShowAddVideo] = useState(false)

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
      const hasProcessingVideos = query.state.data?.some(
        video => video.status !== VideoStatus.COMPLETED && video.status !== VideoStatus.FAILED
      )
      return hasProcessingVideos ? 5000 : false
    }
  })

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

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
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

  if (!videos || videos.length === 0) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">No Videos Yet</h2>
        <p className="text-gray-600 mb-6">Start by processing a video to see it here.</p>
        <Link
          to="/process"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
        >
          Process a Video
        </Link>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Your Videos</h1>
        <AddVideoButton />
      </div>

      {/* Video Player Modal */}
      {selectedVideo && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg w-full max-w-6xl mx-4">
            <div className="p-4 border-b">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold">{selectedVideo.title}</h2>
                <button
                  onClick={() => setSelectedVideo(null)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <div className="aspect-video">
              <VideoPlayer
                url={selectedVideo.url}
                currentTime={currentTime}
                onTimeUpdate={setCurrentTime}
                className="w-full h-full"
              />
            </div>
          </div>
        </div>
      )}

      {/* Video Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-fr">
        {videos.map((video) => (
          video.status === VideoStatus.COMPLETED || video.status === VideoStatus.FAILED ? (
            <Link
              key={video.id}
              to={`/videos/${video.id}`}
              className="block group h-full"
            >
              <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow h-full flex flex-col min-h-[400px]">
                <div className="aspect-video bg-gray-100 relative">
                  {video.thumbnail_url ? (
                    <img
                      src={video.thumbnail_url}
                      alt={video.title || 'Video thumbnail'}
                      className="w-full h-full object-cover bg-gray-100"
                    />
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-200">
                      <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </div>
                  )}
                </div>
                <div className="p-4 flex-1 flex flex-col">
                  <div className="flex justify-between items-start">
                    <h3 className="text-lg font-semibold text-gray-900 line-clamp-3">
                      {video.title || 'Untitled Video'}
                    </h3>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(video.status)}`}
                    >
                      {video.status}
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-gray-500">
                    Added {formatDate(video.created_at)}
                  </p>
                  {video.description && (
                    <p className="mt-3 text-sm text-gray-600 line-clamp-4 flex-1">
                      {video.description}
                    </p>
                  )}
                  {video.metadata?.summary && (
                    <p className="mt-3 text-sm text-gray-600 line-clamp-4 flex-1">
                      {video.metadata.summary}
                    </p>
                  )}
                </div>
              </div>
            </Link>
          ) : null
        ))}
        
        {/* Add skeleton for processing videos */}
        {videos.some(video => 
          video.status !== VideoStatus.COMPLETED && 
          video.status !== VideoStatus.FAILED
        ) && <VideoProcessingSkeleton />}
      </div>

      {/* Progress Modal */}
      {showProgress && (
        <VideoProgressModal
          video={showProgress}
          onClose={() => setShowProgress(null)}
        />
      )}

      {/* Add Video Modal */}
      {showAddVideo && (
        <AddVideoModal onClose={() => setShowAddVideo(false)} />
      )}
    </div>
  )
} 