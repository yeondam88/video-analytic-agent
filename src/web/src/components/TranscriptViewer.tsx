import React from 'react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'

interface TranscriptSegment {
  id: string
  speaker_id: string
  text: string
  start_time: number
  end_time: number
}

interface TranscriptViewerProps {
  transcript: TranscriptSegment[]
}

function formatTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

export function TranscriptViewer({ transcript }: TranscriptViewerProps) {
  if (!transcript?.length) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        Transcript not available
      </div>
    )
  }

  return (
    <ScrollArea className="h-[600px] w-full rounded-md border p-4">
      {transcript.map((segment, index) => (
        <div
          key={segment.id}
          className="mb-4 cursor-pointer hover:bg-muted/50 p-2 rounded-md"
        >
          <div className="flex items-center justify-between text-sm text-muted-foreground mb-1">
            <span>Speaker {segment.speaker_id}</span>
            <span>
              {formatTime(segment.start_time)} - {formatTime(segment.end_time)}
            </span>
          </div>
          <p className="text-foreground">{segment.text}</p>
          {index < transcript.length - 1 && <Separator className="mt-4" />}
        </div>
      ))}
    </ScrollArea>
  )
} 