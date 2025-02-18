import React from 'react'
import { Card } from '@/components/ui/card'

interface Segment {
  id: string
  speaker_id: string
  start_time: number
  end_time: number
}

interface SegmentTimelineProps {
  segments: Segment[]
  duration: number
  currentTime?: number
  onSegmentClick?: (segment: Segment) => void
}

const SPEAKER_COLORS = [
  'bg-blue-500',
  'bg-green-500',
  'bg-yellow-500',
  'bg-purple-500',
  'bg-pink-500',
  'bg-indigo-500',
  'bg-red-500',
  'bg-orange-500'
]

function formatTime(seconds: number): string {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

export function SegmentTimeline({
  segments,
  duration,
  currentTime = 0,
  onSegmentClick
}: SegmentTimelineProps) {
  const speakerIds = Array.from(new Set(segments.map(s => s.speaker_id)))

  return (
    <Card className="p-4">
      <div className="space-y-4">
        {/* Timeline */}
        <div className="relative h-8 bg-muted rounded-md overflow-hidden">
          {segments.map((segment) => {
            const startPercent = (segment.start_time / duration) * 100
            const widthPercent = ((segment.end_time - segment.start_time) / duration) * 100
            const colorIndex = speakerIds.indexOf(segment.speaker_id) % SPEAKER_COLORS.length

            return (
              <div
                key={segment.id}
                className={`absolute h-full cursor-pointer ${SPEAKER_COLORS[colorIndex]} hover:brightness-110 transition-all`}
                style={{
                  left: `${startPercent}%`,
                  width: `${widthPercent}%`
                }}
                onClick={() => onSegmentClick?.(segment)}
                title={`Speaker ${segment.speaker_id}: ${formatTime(segment.start_time)} - ${formatTime(segment.end_time)}`}
              />
            )
          })}
          {/* Current time indicator */}
          {currentTime > 0 && (
            <div
              className="absolute top-0 h-full w-0.5 bg-white shadow-md z-10"
              style={{ left: `${(currentTime / duration) * 100}%` }}
            />
          )}
        </div>

        {/* Time markers */}
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>0:00</span>
          <span>{formatTime(duration)}</span>
        </div>

        {/* Speaker legend */}
        <div className="flex flex-wrap gap-4">
          {speakerIds.map((speakerId, index) => (
            <div key={speakerId} className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${SPEAKER_COLORS[index % SPEAKER_COLORS.length]}`} />
              <span className="text-sm">Speaker {speakerId}</span>
            </div>
          ))}
        </div>
      </div>
    </Card>
  )
} 