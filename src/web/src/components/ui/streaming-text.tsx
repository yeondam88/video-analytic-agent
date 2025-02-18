import React, { useState, useEffect, useCallback, useRef } from 'react'
import { cn } from '@/lib/utils'

interface StreamingTextProps {
  text: string
  delay?: number
  className?: string
  showCursor?: boolean
  playSound?: boolean
  onComplete?: () => void
}

export function StreamingText({
  text,
  delay = 30,
  className,
  showCursor = true,
  playSound = true,
  onComplete
}: StreamingTextProps) {
  const [displayText, setDisplayText] = useState('')
  const audioRef = useRef<HTMLAudioElement | null>(null)

  // Create audio element for typing sound
  useEffect(() => {
    if (playSound) {
      const audio = new Audio('/typing-sound.mp3') // You'll need to add this sound file
      audio.volume = 0.2
      audioRef.current = audio
    }
  }, [playSound])

  // Play typing sound
  const playTypingSound = useCallback(() => {
    if (audioRef.current) {
      const clone = audioRef.current.cloneNode() as HTMLAudioElement
      clone.play()
      // Clean up the cloned audio element after it's done playing
      clone.addEventListener('ended', () => {
        clone.remove()
      })
    }
  }, [])

  useEffect(() => {
    let currentText = ''
    let currentIndex = 0
    
    const typeNextCharacter = () => {
      if (currentIndex < text.length) {
        currentText += text[currentIndex]
        setDisplayText(currentText)
        currentIndex++
        
        if (playSound) {
          playTypingSound()
        }
        
        // Schedule next character
        setTimeout(typeNextCharacter, delay)
      } else {
        onComplete?.()
      }
    }

    // Start typing
    typeNextCharacter()

    // Cleanup
    return () => {
      currentText = ''
      currentIndex = 0
    }
  }, [text, delay, playSound, playTypingSound, onComplete])

  return (
    <span className={cn("relative", className)}>
      {displayText}
      {showCursor && (
        <span
          className={cn(
            "ml-[1px] inline-block h-4 w-[2px] animate-[blink_1s_infinite] bg-current",
            displayText.length === text.length && "animate-none opacity-0"
          )}
          style={{ transition: "opacity 0.1s" }}
        />
      )}
    </span>
  )
} 