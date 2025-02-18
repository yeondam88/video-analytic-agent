import React, { useState, useRef, useEffect } from 'react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'
import { Send } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { motion, AnimatePresence } from 'framer-motion'
import { MessagesList } from '@/components/Messages/MessagesList'
import { Message, MessageType } from '@/components/Messages/types'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'

const containerVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 }
}

// API function to process video
const processVideo = async (url: string) => {
  const response = await fetch("/api/videos/process", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || "Failed to process video");
  }

  return response.json();
};

// API function to chat about videos
const chatWithAssistant = async (message: string) => {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || "Failed to get response");
  }

  return response.json();
};

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)
  const { toast } = useToast()
  const queryClient = useQueryClient()

  // Fetch videos to check if we have any
  const { data: videos } = useQuery({
    queryKey: ['videos'],
    queryFn: async () => {
      const response = await fetch('/api/videos')
      if (!response.ok) {
        throw new Error('Failed to fetch videos')
      }
      return response.json()
    }
  })

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  const processingSteps = {
    video: [
      "Validating Loom video URL...",
      "Extracting video information...",
      "Creating database entry...",
      "Initializing download...",
      "Setting up processing pipeline...",
      "Starting background tasks..."
    ],
    chat: [
      "Thinking...",
      "Processing your request...",
      "Analyzing video content...",
      "Generating response..."
    ]
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    // Check if trying to chat without any videos
    const isVideoUrl = input.includes('loom.com')
    if (!isVideoUrl && (!videos || videos.length === 0)) {
      toast({
        title: "No videos available",
        description: "Please add a video first by pasting a Loom URL",
        variant: "destructive"
      })
      return
    }

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: MessageType.USER,
      content: input,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const steps = isVideoUrl ? processingSteps.video : processingSteps.chat

      // Add processing message
      const processingMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: MessageType.SYSTEM,
        content: steps,
        timestamp: new Date(),
        status: 'processing'
      }
      setMessages(prev => [...prev, processingMessage])

      let response
      if (isVideoUrl) {
        // Process video
        const videoResponse = await processVideo(input)
        response = "🎉 Video processing started! We'll analyze the content and generate insights. You can track the progress in the videos list. This might take a few minutes depending on the video length."
        // Refresh videos list
        queryClient.invalidateQueries({ queryKey: ['videos'] })
      } else {
        // Chat about videos
        response = await chatWithAssistant(input)
      }

      // Remove processing message and add assistant response
      setMessages(prev => {
        const filtered = prev.filter(msg => msg.id !== processingMessage.id)
        return [...filtered, {
          id: (Date.now() + 2).toString(),
          type: MessageType.ASSISTANT,
          content: response,
          timestamp: new Date()
        }]
      })
    } catch (error) {
      // Add error message
      setMessages(prev => {
        const filtered = prev.filter(msg => msg.id !== (Date.now() + 1).toString())
        return [...filtered, {
          id: (Date.now() + 2).toString(),
          type: MessageType.SYSTEM,
          content: error instanceof Error ? error.message : "Failed to process your request. Please try again.",
          timestamp: new Date(),
          status: 'error'
        }]
      })

      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to process request",
        variant: "destructive"
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="flex h-[600px] flex-col">
      <motion.div 
        className="flex items-center justify-between border-b p-4"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="flex items-center space-x-2">
          <span className="text-xl">🤖</span>
          <h2 className="text-lg font-semibold">Video Assistant</h2>
        </div>
      </motion.div>

      <ScrollArea className="flex-1 p-4">
        <AnimatePresence initial={false}>
          <motion.div
            variants={containerVariants}
            initial="initial"
            animate="animate"
            exit="exit"
          >
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground p-4">
                <span className="text-4xl mb-4">👋</span>
                <p className="text-lg font-medium mb-2">Welcome to Video Assistant!</p>
                <p className="max-w-md">
                  {!videos || videos.length === 0 
                    ? "Start by pasting a Loom video URL to process. Once processed, you can ask questions about your videos."
                    : "Ask questions about your videos or paste a new Loom URL to process more videos."}
                </p>
              </div>
            ) : (
              <MessagesList messages={messages} />
            )}
            <div ref={scrollRef} />
          </motion.div>
        </AnimatePresence>
      </ScrollArea>

      <motion.form 
        onSubmit={handleSubmit} 
        className="border-t p-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <div className="flex space-x-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={!videos || videos.length === 0 
              ? "Paste a Loom URL to get started..."
              : "Paste a Loom URL or ask about your videos..."}
            disabled={isLoading}
            className="flex-1"
          />
          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Button 
              type="submit" 
              disabled={isLoading || !input.trim()}
            >
              <Send className="h-4 w-4" />
            </Button>
          </motion.div>
        </div>
      </motion.form>
    </Card>
  )
} 