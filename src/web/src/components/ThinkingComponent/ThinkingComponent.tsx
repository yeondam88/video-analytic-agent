import React, { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { StreamingText } from '../ui/streaming-text'

interface ThinkingComponentProps {
  thoughts: string[]
  onComplete?: () => void
  className?: string
  showDots?: boolean
  delay?: number
}

export function ThinkingComponent({
  thoughts,
  onComplete,
  className,
  showDots = true,
  delay = 30
}: ThinkingComponentProps) {
  const [currentThoughtIndex, setCurrentThoughtIndex] = useState(0)
  const [isComplete, setIsComplete] = useState(false)
  const [dots, setDots] = useState('.')

  // Animate the thinking dots
  useEffect(() => {
    if (!showDots || isComplete) return

    const intervalId = setInterval(() => {
      setDots(prev => prev.length < 3 ? prev + '.' : '.')
    }, 500)

    return () => clearInterval(intervalId)
  }, [showDots, isComplete])

  // Handle thought completion
  const handleThoughtComplete = () => {
    if (currentThoughtIndex < thoughts.length - 1) {
      setCurrentThoughtIndex(prev => prev + 1)
    } else {
      setIsComplete(true)
      onComplete?.()
    }
  }

  return (
    <div className={cn("space-y-4", className)}>
      {thoughts.slice(0, currentThoughtIndex + 1).map((thought, index) => (
        <div
          key={index}
          className={cn(
            "p-4 rounded-lg",
            index === currentThoughtIndex && !isComplete
              ? "bg-blue-50 text-blue-700"
              : "bg-gray-50 text-gray-700"
          )}
        >
          <div className="flex items-start gap-2">
            <span className="mt-1.5">💭</span>
            <div className="flex-1">
              {index === currentThoughtIndex && !isComplete ? (
                <>
                  <StreamingText
                    text={thought}
                    delay={delay}
                    onComplete={handleThoughtComplete}
                    className="block"
                  />
                  {showDots && <span className="text-blue-500">{dots}</span>}
                </>
              ) : (
                <span>{thought}</span>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
} 