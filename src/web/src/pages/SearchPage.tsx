import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Input } from '@/components/ui/input'
import { VideoGrid } from '@/components/VideoGrid'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { ReloadIcon } from '@radix-ui/react-icons'
import { useDebounce } from '@/lib/hooks'

export function SearchPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const debouncedQuery = useDebounce(searchQuery, 500)

  const {
    data: videos,
    isLoading,
    isError,
    error,
    refetch
  } = useQuery({
    queryKey: ['search', debouncedQuery],
    queryFn: async () => {
      if (!debouncedQuery) return []
      const response = await fetch(`/api/search?q=${encodeURIComponent(debouncedQuery)}`)
      if (!response.ok) {
        throw new Error('Failed to search videos')
      }
      return response.json()
    },
    enabled: Boolean(debouncedQuery)
  })

  if (isError) {
    return (
      <div className="space-y-4">
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {error instanceof Error ? error.message : 'Failed to search videos'}
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
      <Input
        type="search"
        placeholder="Search videos..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="max-w-sm"
      />
      {debouncedQuery && (
        <VideoGrid videos={videos || []} isLoading={isLoading} />
      )}
    </div>
  )
} 