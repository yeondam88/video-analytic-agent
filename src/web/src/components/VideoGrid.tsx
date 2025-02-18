import React from 'react'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Video, VideoStatus } from '@/types/video'

interface VideoGridProps {
  videos: Video[]
  isLoading: boolean
}

const getStatusColor = (status: VideoStatus) => {
  switch (status) {
    case 'TRANSCRIBED':
      return 'bg-green-500 hover:bg-green-600'
    case 'FAILED':
      return 'bg-red-500 hover:bg-red-600'
    case 'PENDING':
      return 'bg-yellow-500 hover:bg-yellow-600'
    default:
      return 'bg-blue-500 hover:bg-blue-600'
  }
}

const getStatusText = (status: VideoStatus): string => {
  return status.charAt(0) + status.slice(1).toLowerCase().replace(/_/g, ' ')
}

export function VideoGrid({ videos, isLoading }: VideoGridProps) {
  if (isLoading) {
    return (
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, i) => (
          <Card key={i} className="overflow-hidden">
            <CardHeader className="p-0">
              <Skeleton className="aspect-video w-full" />
            </CardHeader>
            <CardContent className="p-4">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="mt-2 h-4 w-1/2" />
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (!videos.length) {
    return (
      <div className="text-center p-8">
        <p className="text-muted-foreground">No videos found</p>
        <p className="text-sm text-muted-foreground mt-2">
          Add a new video by entering a Loom URL above.
        </p>
      </div>
    )
  }

  return (
    <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {videos.map((video) => (
        <Link key={video.id} to={`/videos/${video.id}`}>
          <Card className="overflow-hidden transition-all hover:shadow-lg hover:scale-[1.02]">
            <CardHeader className="p-0">
              <div className="relative">
                <img
                  src={video.thumbnail_url || '/placeholder-video.png'}
                  alt={video.title}
                  className="aspect-video w-full object-cover"
                />
                {video.duration && (
                  <div className="absolute bottom-2 right-2 bg-black/75 text-white px-2 py-1 rounded text-xs">
                    {formatDuration(video.duration)}
                  </div>
                )}
              </div>
            </CardHeader>
            <CardContent className="p-4">
              <CardTitle className="line-clamp-2 mb-2">{video.title || 'Untitled Video'}</CardTitle>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Badge className={`${getStatusColor(video.status)} transition-colors`}>
                    {getStatusText(video.status)}
                  </Badge>
                  <span className="text-sm text-muted-foreground">
                    {new Date(video.created_at).toLocaleDateString()}
                  </span>
                </div>
                {video.status !== 'TRANSCRIBED' && video.status !== 'FAILED' && (
                  <div className="space-y-1">
                    <Progress value={video.progress} className="h-2" />
                    <p className="text-xs text-muted-foreground text-right">
                      {Math.round(video.progress)}%
                    </p>
                  </div>
                )}
                {video.error && (
                  <p className="text-sm text-red-500 line-clamp-2" title={video.error}>
                    {video.error}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  )
}

function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
} 