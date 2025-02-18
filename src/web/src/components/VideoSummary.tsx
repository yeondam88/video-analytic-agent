import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { ReloadIcon } from '@radix-ui/react-icons'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

interface Summary {
  content: string
  key_points: string[]
  action_items?: string[]
  sentiment?: string
}

interface VideoSummaryProps {
  videoId: string
}

export function VideoSummary({ videoId }: VideoSummaryProps) {
  const {
    data: summary,
    isLoading,
    isError,
    error,
    refetch
  } = useQuery({
    queryKey: ['summary', videoId],
    queryFn: async () => {
      const response = await fetch(`/api/videos/${videoId}/summary`)
      if (!response.ok) {
        throw new Error('Failed to fetch summary')
      }
      return response.json() as Promise<Summary>
    }
  })

  if (isError) {
    return (
      <div className="space-y-4">
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {error instanceof Error ? error.message : 'Failed to load summary'}
          </AlertDescription>
        </Alert>
        <Button onClick={() => refetch()} variant="outline">
          <ReloadIcon className="mr-2 h-4 w-4" />
          Try again
        </Button>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="animate-pulse bg-muted h-4 w-1/3 rounded" />
          </CardHeader>
          <CardContent className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="animate-pulse bg-muted h-4 w-full rounded" />
            ))}
          </CardContent>
        </Card>
      </div>
    )
  }

  if (!summary) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No summary available
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm">{summary.content}</p>
        </CardContent>
      </Card>

      {/* Key Points */}
      <Card>
        <CardHeader>
          <CardTitle>Key Points</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="list-disc list-inside space-y-2">
            {summary.key_points.map((point, index) => (
              <li key={index} className="text-sm">{point}</li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* Action Items */}
      {summary.action_items && summary.action_items.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Action Items</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc list-inside space-y-2">
              {summary.action_items.map((item, index) => (
                <li key={index} className="text-sm">{item}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Sentiment */}
      {summary.sentiment && (
        <Card>
          <CardHeader>
            <CardTitle>Overall Sentiment</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{summary.sentiment}</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
} 