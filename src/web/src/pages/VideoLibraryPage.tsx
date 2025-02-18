import React, { useState, useEffect } from 'react'
import { VideoList } from '@/components/VideoList'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useToast } from '@/components/ui/use-toast'
import { Video } from '@/types'
import { api } from '@/lib/api'

export function VideoLibraryPage() {
  const [videos, setVideos] = useState<Video[]>([])
  const [loading, setLoading] = useState(true)
  const [newVideoId, setNewVideoId] = useState('')
  const { toast } = useToast()

  useEffect(() => {
    fetchVideos()
    // Poll for updates every 5 seconds
    const interval = setInterval(fetchVideos, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchVideos = async () => {
    try {
      const response = await api.get<Video[]>('/videos')
      setVideos(response.data)
    } catch (error) {
      console.error('Error fetching videos:', error)
      toast({
        title: 'Error',
        description: 'Failed to fetch videos',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const handleAddVideo = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newVideoId.trim()) return

    try {
      await api.post('/videos', {
        loom_video_id: newVideoId,
        status: 'pending',
        to_process: true,
      })
      setNewVideoId('')
      toast({
        title: 'Success',
        description: 'Video added successfully',
      })
      await fetchVideos()
    } catch (error) {
      console.error('Error adding video:', error)
      toast({
        title: 'Error',
        description: 'Failed to add video',
        variant: 'destructive',
      })
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Video Library</h1>
      </div>

      <div className="bg-card rounded-lg p-6 shadow-sm">
        <h2 className="text-lg font-semibold mb-4">Add New Video</h2>
        <form onSubmit={handleAddVideo} className="flex gap-4">
          <Input
            type="text"
            value={newVideoId}
            onChange={(e) => setNewVideoId(e.target.value)}
            placeholder="Enter Loom video ID"
            className="flex-1"
          />
          <Button type="submit">Add Video</Button>
        </form>
      </div>

      {videos.length > 0 ? (
        <VideoList videos={videos} />
      ) : (
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-muted-foreground">
            No videos yet
          </h3>
          <p className="text-sm text-muted-foreground mt-1">
            Add your first video to get started
          </p>
        </div>
      )}
    </div>
  )
} 