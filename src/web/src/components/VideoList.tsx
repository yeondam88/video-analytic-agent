import React from 'react'
import { Link } from 'react-router-dom'
import { Video } from '@/types'
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useNavigate } from 'react-router-dom'

interface VideoListProps {
  videos: Video[]
}

export function VideoList({ videos }: VideoListProps) {
  const navigate = useNavigate()

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {videos.map((video) => (
        <Card key={video.id} className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="relative aspect-video w-full mb-4">
              {video.thumbnail_url ? (
                <img
                  src={video.thumbnail_url}
                  alt={video.title || 'Video thumbnail'}
                  className="rounded-md object-cover w-full h-full"
                />
              ) : (
                <div className="w-full h-full bg-muted flex items-center justify-center rounded-md">
                  <span className="text-muted-foreground">No thumbnail</span>
                </div>
              )}
            </div>
            <CardTitle>{video.title || 'Untitled Video'}</CardTitle>
            <CardDescription>
              {video.description || 'No description available'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span
                className={`px-2 py-1 rounded-full text-xs font-medium ${
                  video.status === 'completed'
                    ? 'bg-green-100 text-green-800'
                    : video.status === 'failed'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}
              >
                {video.status}
              </span>
              <span className="text-sm text-muted-foreground">
                {new Date(video.created_at).toLocaleDateString()}
              </span>
            </div>
          </CardContent>
          <CardFooter>
            <Button
              variant="secondary"
              className="w-full"
              onClick={() => navigate(`/videos/${video.id}`)}
            >
              View Details
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  )
} 