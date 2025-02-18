import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useMutation, useQueryClient, useQuery } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { useState, useEffect } from "react";

import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { MessagesList } from "./Messages/MessagesList";
import { Message, MessageType } from "./Messages/types";
import { Progress } from "./ui/progress";
import { VideoStatus, VideoResponse, processingSteps } from "@/types/video";

// Form validation schema
const videoFormSchema = z.object({
  url: z.string().url("Please enter a valid URL").refine(
    (url) => url.includes("loom.com") || url.includes("youtube.com") || url.includes("youtu.be"),
    "Only Loom and YouTube video URLs are supported"
  ),
});

type VideoFormValues = z.infer<typeof videoFormSchema>;

// API functions
const processVideo = async (url: string): Promise<VideoResponse> => {
  const response = await fetch("/api/videos/process", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to process video");
  }

  return response.json();
};

const getVideoStatus = async (videoId: number): Promise<VideoResponse> => {
  const response = await fetch(`/api/videos/${videoId}`);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to get video status");
  }
  return response.json();
};

export function VideoInputForm() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [processingVideoId, setProcessingVideoId] = useState<number | null>(null);
  const queryClient = useQueryClient();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<VideoFormValues>({
    resolver: zodResolver(videoFormSchema),
  });

  // Query for polling video status
  const { data: videoStatus } = useQuery({
    queryKey: ['video', processingVideoId],
    queryFn: () => processingVideoId ? getVideoStatus(processingVideoId) : null,
    enabled: !!processingVideoId,
    refetchInterval: (query) => {
      const data = query.state.data as VideoResponse | null;
      if (data?.status === 'TRANSCRIBED' || data?.status === 'FAILED') {
        setProcessingVideoId(null);
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
  });

  // Update messages when video status changes
  useEffect(() => {
    if (videoStatus) {
      // Add status message
      const statusMessage = getStatusMessage(videoStatus);
      if (statusMessage) {
        setMessages(prev => {
          const lastMessage = prev[prev.length - 1];
          if (lastMessage?.content !== statusMessage) {
            return [...prev, {
              id: Date.now().toString(),
              type: MessageType.SYSTEM,
              content: statusMessage,
              timestamp: new Date(),
              status: videoStatus.status === 'FAILED' ? 'error' : 
                     videoStatus.status === 'TRANSCRIBED' ? 'success' : 
                     'processing'
            }];
          }
          return prev;
        });
      }

      // Handle completion
      if (videoStatus.status === 'TRANSCRIBED') {
        toast.success('Video processing completed! 🎉');
        queryClient.invalidateQueries({ queryKey: ['videos'] });
      }
      // Handle failure
      else if (videoStatus.status === 'FAILED') {
        toast.error(videoStatus.error || 'Video processing failed');
      }
    }
  }, [videoStatus, queryClient]);

  const { mutate, isPending } = useMutation({
    mutationFn: (values: VideoFormValues) => {
      // Reset state
      setMessages([]);
      
      // Add initial message
      setMessages([{
        id: Date.now().toString(),
        type: MessageType.USER,
        content: `Processing video: ${values.url}`,
        timestamp: new Date(),
      }]);

      toast.loading('Starting video processing...', { id: 'processing' });
      return processVideo(values.url);
    },
    onSuccess: (data) => {
      setProcessingVideoId(data.id);
      reset();
      toast.success('Video processing started!', { id: 'processing' });
    },
    onError: (error: Error) => {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        type: MessageType.SYSTEM,
        content: `❌ ${error.message}`,
        timestamp: new Date(),
        status: 'error'
      }]);
      toast.error(error.message, { id: 'processing' });
    },
  });

  const getStatusMessage = (video: VideoResponse): string => {
    if (video.status === 'FAILED') {
      return `❌ Processing failed: ${video.error}`;
    }
    
    const currentStep = processingSteps.find(step => 
      video.steps_completed.includes(step.id) && 
      step.status === video.status
    );
    
    if (currentStep) {
      return `🔄 ${currentStep.label} (${Math.round(video.progress)}%)`;
    }
    
    return '';
  };

  const onSubmit = (values: VideoFormValues) => {
    mutate(values);
  };

  const isProcessing = isPending || !!processingVideoId;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Process New Video</CardTitle>
        <CardDescription>
          Enter a Loom or YouTube video URL to analyze its content and generate insights.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="flex gap-4">
            <Input
              placeholder="Enter Loom video URL"
              {...register("url")}
              disabled={isProcessing}
              className="flex-1"
            />
            <Button 
              type="submit" 
              disabled={isProcessing}
              className="min-w-[120px]"
            >
              {isProcessing ? "Processing..." : "Process"}
            </Button>
          </div>
          
          {errors.url && (
            <p className="text-sm text-red-500">{errors.url.message}</p>
          )}
          
          {videoStatus && (
            <div className="space-y-4 mt-6 p-4 bg-muted rounded-lg">
              <Progress value={videoStatus.progress} />
              <div className="space-y-2">
                {processingSteps.map((step) => {
                  const isCompleted = videoStatus.steps_completed.includes(step.id);
                  const isCurrent = videoStatus.status === step.status &&
                                  videoStatus.steps_completed.includes(step.id);
                  
                  return (
                    <div
                      key={step.id}
                      className={`flex items-center gap-2 ${
                        isCompleted ? 'text-primary' : 'text-muted-foreground'
                      } ${isCurrent ? 'font-bold' : ''}`}
                    >
                      {isCompleted ? '✓' : '○'} {step.label}
                      {isCurrent && ' (Current)'}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
          
          {messages.length > 0 && (
            <div className="mt-6">
              <MessagesList messages={messages} />
            </div>
          )}
        </form>
      </CardContent>
    </Card>
  );
} 