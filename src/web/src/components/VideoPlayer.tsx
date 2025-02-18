import React, { useEffect, useRef, useState, useMemo } from 'react';
import YouTube from 'react-youtube';
import { logger } from '../utils/logger';

interface VideoPlayerProps {
  url: string;
  currentTime?: number;
  onTimeUpdate?: (time: number) => void;
  onReady?: () => void;
  onStateChange?: (event: { data: number }) => void;
  className?: string;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({
  url,
  currentTime = 0,
  onTimeUpdate,
  onReady,
  onStateChange,
  className = ''
}) => {
  const [player, setPlayer] = useState<any>(null);
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const loomPlayerRef = useRef<HTMLIFrameElement>(null);
  const initialSeekPending = useRef(true);
  const lastSeekTime = useRef<number>(currentTime);
  const timeUpdateIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const seekTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isSeekingRef = useRef<boolean>(false);
  const lastReportedTimeRef = useRef<number>(0);
  
  // Memoize video ID extraction to prevent infinite re-renders
  const { videoId, isYouTube, isLoom } = useMemo(() => {
    try {
      // YouTube URL patterns
      const youtubePatterns = [
        /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/
      ];
      
      let extractedId: string | undefined;
      let isYT = false;
      let isLm = false;
      
      // Check for YouTube
      for (const pattern of youtubePatterns) {
        const match = url.match(pattern);
        if (match) {
          extractedId = match[1];
          isYT = true;
          logger.info(`Extracted YouTube video ID: ${extractedId} from URL: ${url}`);
          break;
        }
      }
      
      // Check for Loom if not YouTube
      if (!extractedId) {
        const loomMatch = url.match(/(?:https?:\/\/)?(?:www\.)?loom\.com\/share\/([a-zA-Z0-9]+)/);
        if (loomMatch) {
          extractedId = loomMatch[1];
          isLm = true;
          logger.info(`Extracted Loom video ID: ${extractedId} from URL: ${url}`);
        }
      }
      
      if (!extractedId) {
        logger.warn(`No video ID found for URL: ${url}`);
      }
      
      return {
        videoId: extractedId,
        isYouTube: isYT,
        isLoom: isLm
      };
    } catch (e) {
      logger.error(`Error extracting video ID: ${e}`);
      return {
        videoId: undefined,
        isYouTube: false,
        isLoom: false
      };
    }
  }, [url]);

  useEffect(() => {
    if (isLoom && videoId) {
      // Setup Loom player
      const setupLoomPlayer = () => {
        if (!window.loomPlayer && loomPlayerRef.current) {
          window.loomPlayer = window.LoomPlayer && window.LoomPlayer.init({
            element: loomPlayerRef.current
          });
          
          window.loomPlayer?.on('ready', () => {
            logger.info('Loom player ready');
            setIsReady(true);
            if (onReady) onReady();
          });
          
          window.loomPlayer?.on('timeupdate', (time: number) => {
            if (onTimeUpdate) onTimeUpdate(Math.floor(time));
          });
          
          window.loomPlayer?.on('error', (error: any) => {
            logger.error(`Loom player error: ${error}`);
            setError(`Loom player error: ${error}`);
          });
        }
      };

      // Load Loom SDK if not already loaded
      if (!document.querySelector('script[src*="sdk.loom.com"]')) {
        const script = document.createElement('script');
        script.src = 'https://sdk.loom.com/player';
        script.async = true;
        script.onload = setupLoomPlayer;
        script.onerror = (e) => {
          logger.error(`Failed to load Loom SDK: ${e}`);
          setError('Failed to load Loom player');
        };
        document.body.appendChild(script);
      } else {
        setupLoomPlayer();
      }
    }
  }, [isLoom, videoId, onReady, onTimeUpdate]);

  // Handle YouTube player ready
  const onYouTubePlayerReady = (event: any) => {
    try {
      logger.info('YouTube player ready');
      const youtubePlayer = event.target;
      setPlayer(youtubePlayer);
      setIsReady(true);
      setError(null);
      
      // Clear existing interval if any
      if (timeUpdateIntervalRef.current) {
        clearInterval(timeUpdateIntervalRef.current);
      }
      
      // Set up interval for time updates
      timeUpdateIntervalRef.current = setInterval(() => {
        try {
          if (!isSeekingRef.current) {
            const currentPlayerTime = Math.floor(youtubePlayer.getCurrentTime());
            if (currentPlayerTime !== lastReportedTimeRef.current) {
              lastReportedTimeRef.current = currentPlayerTime;
              if (onTimeUpdate) onTimeUpdate(currentPlayerTime);
            }
          }
        } catch (error) {
          logger.error(`Failed to get current time: ${error}`);
        }
      }, 200);
      
      if (onReady) onReady();
      
      // Initial seek if needed
      if (currentTime > 0) {
        logger.info(`Initial seek to ${currentTime}s`);
        isSeekingRef.current = true;
        if (seekTimeoutRef.current) {
          clearTimeout(seekTimeoutRef.current);
        }
        seekTimeoutRef.current = setTimeout(() => {
          try {
            youtubePlayer.seekTo(currentTime, true);
            youtubePlayer.playVideo();
            setIsPlaying(true);
            isSeekingRef.current = false;
          } catch (error) {
            logger.error(`Failed to perform initial seek: ${error}`);
            isSeekingRef.current = false;
          }
        }, 500);
      }
    } catch (e) {
      logger.error(`Error in YouTube player ready handler: ${e}`);
      setError(`Failed to initialize YouTube player: ${e}`);
    }
  };

  // Handle YouTube player state changes
  const onYouTubePlayerStateChange = (event: any) => {
    try {
      logger.info(`YouTube player state changed: ${event.data}`);
      // YT.PlayerState values: -1 (unstarted) | 0 (ended) | 1 (playing) | 2 (paused) | 3 (buffering) | 5 (video cued)
      if (event.data === 1) {
        logger.info('YouTube player started playing');
        setIsPlaying(true);
        if (onStateChange) {
          onStateChange(event);
        }
      } else if (event.data === 2) {
        setIsPlaying(false);
      }
      
      // Only handle seeking if it's an explicit seek operation
      if (isSeekingRef.current && event.data === 1) {
        isSeekingRef.current = false;
      }
    } catch (error) {
      logger.error(`Failed to handle state change: ${error}`);
    }
  };

  // Handle YouTube player errors
  const onYouTubePlayerError = (event: any) => {
    let errorMessage = 'Unknown YouTube player error';
    
    // YouTube error codes
    switch (event.data) {
      case 2:
        errorMessage = 'Invalid YouTube video ID';
        break;
      case 5:
        errorMessage = 'HTML5 player error';
        break;
      case 100:
        errorMessage = 'Video not found or removed';
        break;
      case 101:
      case 150:
        errorMessage = 'Video playback not allowed';
        break;
    }
    
    logger.error(`YouTube player error: ${errorMessage} (code: ${event.data})`);
    setError(errorMessage);
  };

  // Handle seeking
  useEffect(() => {
    if (isReady && currentTime !== lastSeekTime.current && Math.abs(currentTime - lastReportedTimeRef.current) > 1) {
      try {
        lastSeekTime.current = currentTime;
        if (isYouTube && player) {
          logger.info(`Seeking YouTube player to ${currentTime}s`);
          isSeekingRef.current = true;
          if (seekTimeoutRef.current) {
            clearTimeout(seekTimeoutRef.current);
          }
          seekTimeoutRef.current = setTimeout(() => {
            try {
              player.seekTo(currentTime, true);
              if (isPlaying) {
                player.playVideo();
              }
              logger.info(`Successfully seeked to ${currentTime}s`);
              isSeekingRef.current = false;
            } catch (error) {
              logger.error(`Failed to seek and play: ${error}`);
              setError(`Failed to seek to ${currentTime}s: ${error}`);
              isSeekingRef.current = false;
            }
          }, 200);
        } else if (isLoom && window.loomPlayer) {
          window.loomPlayer.seekTo(currentTime);
          if (isPlaying) {
            window.loomPlayer.play();
          }
          logger.info(`Seeking Loom player to ${currentTime}s`);
        }
      } catch (error) {
        logger.error(`Failed to seek to time ${currentTime}: ${error}`);
        setError(`Failed to seek to ${currentTime}s: ${error}`);
        isSeekingRef.current = false;
      }
    }
  }, [currentTime, isReady, player, isYouTube, isLoom, isPlaying]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeUpdateIntervalRef.current) {
        clearInterval(timeUpdateIntervalRef.current);
      }
      if (seekTimeoutRef.current) {
        clearTimeout(seekTimeoutRef.current);
      }
    };
  }, []);

  if (!videoId) {
    return (
      <div className={`flex items-center justify-center bg-gray-100 ${className}`}>
        <span className="text-gray-500">Invalid video URL</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex items-center justify-center bg-gray-100 ${className}`}>
        <span className="text-red-500">{error}</span>
      </div>
    );
  }

  if (isYouTube) {
    return (
      <YouTube
        videoId={videoId}
        className={className}
        opts={{
          height: '100%',
          width: '100%',
          playerVars: {
            autoplay: 1,
            modestbranding: 1,
            rel: 0,
            origin: window.location.origin,
            enablejsapi: 1,
            playsinline: 1,
            controls: 1
          }
        }}
        onReady={onYouTubePlayerReady}
        onStateChange={onYouTubePlayerStateChange}
        onError={onYouTubePlayerError}
      />
    );
  }

  if (isLoom) {
    return (
      <iframe
        ref={loomPlayerRef}
        src={`https://www.loom.com/embed/${videoId}`}
        className={`${className} border-0`}
        allowFullScreen
      />
    );
  }

  return (
    <div className={`flex items-center justify-center bg-gray-100 ${className}`}>
      <span className="text-gray-500">Unsupported video source</span>
    </div>
  );
};

// Add TypeScript type definition for Loom SDK
declare global {
  interface Window {
    LoomPlayer?: {
      init: (config: { element: HTMLIFrameElement }) => any;
    };
    loomPlayer?: any;
  }
} 