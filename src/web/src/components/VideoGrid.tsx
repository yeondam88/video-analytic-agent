import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Video, VideoStatus, VideoSource } from '@/types/video'
import { Tab } from '@headlessui/react'
import { cn } from '@/lib/utils'

interface VideoGridProps {
  videos: Array<{
    id: string;
    title: string;
    thumbnail_url: string;
    duration: number;
    status: string;
    progress: number;
    source: VideoSource;
    created_at: string;
    error?: string;
  }>;
  isLoading?: boolean;
}

const getStatusColor = (status: VideoStatus) => {
  switch (status) {
    case VideoStatus.COMPLETED:
      return 'bg-green-500 hover:bg-green-600'
    case VideoStatus.FAILED:
      return 'bg-red-500 hover:bg-red-600'
    case VideoStatus.PENDING:
      return 'bg-yellow-500 hover:bg-yellow-600'
    default:
      return 'bg-blue-500 hover:bg-blue-600'
  }
}

const getStatusText = (status: VideoStatus): string => {
  return status.charAt(0) + status.slice(1).toLowerCase().replace(/_/g, ' ')
}

export function VideoGrid({ videos, isLoading }: VideoGridProps) {
  const [selectedTab, setSelectedTab] = useState(0)
  
  // Group videos by source
  const videosBySource = {
    ALL: videos,
    YOUTUBE: videos.filter(v => v.source === VideoSource.YOUTUBE),
    LOOM: videos.filter(v => v.source === VideoSource.LOOM),
  }

  const tabs = [
    { name: 'All Videos', key: 'ALL', count: videos.length },
    { name: 'YouTube Videos', key: 'YOUTUBE', count: videosBySource.YOUTUBE.length },
    { name: 'Loom Videos', key: 'LOOM', count: videosBySource.LOOM.length },
  ]

  return (
    <div className="w-full">
      <Tab.Group onChange={setSelectedTab}>
        <Tab.List className="flex border-b border-gray-200 mb-6">
          {tabs.map((tab) => (
            <Tab
              key={tab.key}
              className={({ selected }) =>
                cn(
                  'px-6 py-3 text-sm font-medium leading-5 text-gray-500 transition-colors relative',
                  'focus:outline-none hover:text-gray-700',
                  selected && [
                    'text-blue-600',
                    'after:absolute after:bottom-0 after:left-0 after:right-0',
                    'after:h-0.5 after:bg-blue-600 after:rounded-t-full'
                  ]
                )
              }
            >
              <span className="flex items-center gap-2">
                {tab.name}
                <span className="text-xs font-normal text-gray-400">
                  ({tab.count})
                </span>
              </span>
            </Tab>
          ))}
        </Tab.List>
        <Tab.Panels>
          {tabs.map((tab) => (
            <Tab.Panel key={tab.key}>
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {videosBySource[tab.key as keyof typeof videosBySource].map((video) => (
                  <Link key={video.id} to={`/videos/${video.id}`}>
                    <Card className="overflow-hidden transition-all hover:shadow-lg">
                      <CardHeader className="p-0">
                        <div className="relative aspect-video">
                          <img
                            src={video.thumbnail_url || '/placeholder-video.png'}
                            alt={video.title}
                            className="w-full h-full object-cover"
                          />
                          {video.duration > 0 && (
                            <div className="absolute bottom-2 right-2 bg-black/75 text-white px-2 py-1 rounded text-xs">
                              {formatDuration(video.duration)}
                            </div>
                          )}
                        </div>
                      </CardHeader>
                      <CardContent className="p-4">
                        <CardTitle className="text-base font-medium line-clamp-2 mb-2">
                          {video.title || 'Untitled Video'}
                        </CardTitle>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <Badge variant="secondary" className="text-xs font-normal">
                              {getStatusText(video.status as VideoStatus)}
                            </Badge>
                            <span className="text-xs text-gray-500">
                              {new Date(video.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          {video.status !== VideoStatus.COMPLETED && 
                           video.status !== VideoStatus.FAILED && (
                            <div className="space-y-1">
                              <Progress value={video.progress} className="h-1.5" />
                              <p className="text-xs text-gray-500 text-right">
                                {Math.round(video.progress)}%
                              </p>
                            </div>
                          )}
                          {video.error && (
                            <p className="text-xs text-red-500 line-clamp-2" title={video.error}>
                              {video.error}
                            </p>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </Link>
                ))}
              </div>
              {videosBySource[tab.key as keyof typeof videosBySource].length === 0 && (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <p className="text-gray-500 mb-2">No videos found</p>
                  <p className="text-sm text-gray-400">
                    Add a new video by entering a {tab.key === 'YOUTUBE' ? 'YouTube' : 'Loom'} URL
                  </p>
                </div>
              )}
            </Tab.Panel>
          ))}
        </Tab.Panels>
      </Tab.Group>
    </div>
  )
}

function formatDuration(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}