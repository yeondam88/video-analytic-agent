import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Input } from '@/components/ui/input'
import { VideoGrid } from '@/components/VideoGrid'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { ReloadIcon } from '@radix-ui/react-icons'
import { useDebounce } from '@/lib/hooks'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Card, CardContent } from '@/components/ui/card'

interface SegmentResult {
  id: string
  video_id: string
  text: string
  start_time: number
  end_time: number
  similarity: number
}

export function SearchPage() {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedSource, setSelectedSource] = useState<string>('')
  const [searchType, setSearchType] = useState<'videos' | 'segments'>('videos')
  const debouncedQuery = useDebounce(searchQuery, 500)

  const {
    data: searchResults,
    isLoading,
    isError,
    error,
    refetch
  } = useQuery({
    queryKey: ['search', searchType, debouncedQuery, selectedSource],
    queryFn: async () => {
      if (!debouncedQuery) return { results: [], count: 0, query: '' }
      
      if (searchType === 'videos') {
        const response = await fetch('/api/search/basic', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            query: debouncedQuery,
            limit: 20,
            filters: {
              ...(selectedSource && { source: selectedSource })
            }
          })
        })
        
        if (!response.ok) {
          throw new Error('Failed to search videos')
        }
        return response.json()
      } else {
        const response = await fetch(`/api/search/segments?query=${encodeURIComponent(debouncedQuery)}&limit=20&threshold=0.5`)
        
        if (!response.ok) {
          throw new Error('Failed to search segments')
        }
        const segments = await response.json()
        return {
          results: segments,
          count: segments.length,
          query: debouncedQuery
        }
      }
    },
    enabled: Boolean(debouncedQuery)
  })

  const handleSegmentClick = (segment: SegmentResult) => {
    navigate(`/videos/${segment.video_id}?start=${segment.start_time}&end=${segment.end_time}`)
  }

  if (isError) {
    return (
      <div className="space-y-4">
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {error instanceof Error ? error.message : 'Failed to search'}
          </AlertDescription>
        </Alert>
        <Button onClick={() => refetch()} variant="outline">
          <ReloadIcon className="mr-2 h-4 w-4" />
          Try again
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Search</h1>
      </div>
      
      <div className="flex gap-4">
        <Input
          type="search"
          placeholder="Search videos..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="max-w-sm"
        />
        <Select value={searchType} onValueChange={(value: 'videos' | 'segments') => setSearchType(value)}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Search Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="videos">Videos</SelectItem>
            <SelectItem value="segments">Segments</SelectItem>
          </SelectContent>
        </Select>
        {searchType === 'videos' && (
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
        )}
      </div>

      {debouncedQuery && searchResults && (
        <>
          <div className="text-sm text-muted-foreground">
            Found {searchResults.count} results for "{searchResults.query}"
          </div>
          {searchType === 'videos' ? (
            <VideoGrid videos={searchResults.results || []} isLoading={isLoading} />
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {searchResults.results.map((segment: SegmentResult) => (
                <Card
                  key={segment.id}
                  className="cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => handleSegmentClick(segment)}
                >
                  <CardContent className="p-4">
                    <div className="flex justify-between items-start mb-2">
                      <div className="text-sm text-muted-foreground">
                        {Math.floor(segment.start_time / 60)}:{String(Math.floor(segment.start_time % 60)).padStart(2, '0')} - {Math.floor(segment.end_time / 60)}:{String(Math.floor(segment.end_time % 60)).padStart(2, '0')}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {Math.round(segment.similarity * 100)}% match
                      </div>
                    </div>
                    <p className="text-sm">{segment.text}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
} 