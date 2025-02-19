import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Input } from '@/components/ui/input'
import { VideoGrid } from '@/components/VideoGrid'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { ReloadIcon } from '@radix-ui/react-icons'
import { useDebounce } from '@/lib/hooks'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

export function SearchPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedSource, setSelectedSource] = useState<string>('')
  const debouncedQuery = useDebounce(searchQuery, 500)

  const {
    data: searchResults,
    isLoading,
    isError,
    error,
    refetch
  } = useQuery({
    queryKey: ['search', debouncedQuery, selectedSource],
    queryFn: async () => {
      if (!debouncedQuery) return { results: [], count: 0, query: '' }
      
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
      
      <div className="flex gap-4">
        <Input
          type="search"
          placeholder="Search videos..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="max-w-sm"
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

      {debouncedQuery && searchResults && (
        <>
          <div className="text-sm text-muted-foreground">
            Found {searchResults.count} results for "{searchResults.query}"
          </div>
          <VideoGrid videos={searchResults.results || []} isLoading={isLoading} />
        </>
      )}
    </div>
  )
} 