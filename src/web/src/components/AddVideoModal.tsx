import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { logger } from '../utils/logger';
import { VideoProcessingSkeleton } from './VideoProcessingSkeleton';
import { motion, AnimatePresence } from 'framer-motion';

interface AddVideoModalProps {
  onClose: () => void;
}

export const AddVideoModal: React.FC<AddVideoModalProps> = ({ onClose }) => {
  const [urls, setUrls] = useState<string[]>(['']);
  const [error, setError] = useState<string | null>(null);
  const [showProcessing, setShowProcessing] = useState(false);
  const queryClient = useQueryClient();

  const addVideoMutation = useMutation({
    mutationFn: async (urls: string[]) => {
      const response = await fetch('/api/queue', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          urls,
          priority: 0,
          metadata: {
            source: 'bulk_upload'
          }
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to add videos');
      }

      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['videos'] });
      setShowProcessing(true);
      // Keep modal open for 2 seconds to show processing state
      setTimeout(() => {
        onClose();
      }, 2000);
    },
    onError: (error: Error) => {
      logger.error('Failed to add videos:', error);
      setError(error.message);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    // Filter out empty URLs and validate
    const validUrls = urls.filter(url => url.trim()).map(url => url.trim());
    
    if (validUrls.length === 0) {
      setError('Please enter at least one valid URL');
      return;
    }
    
    // Validate URLs
    const invalidUrls = validUrls.filter(url => {
      try {
        const parsed = new URL(url);
        return !(
          parsed.hostname.includes('youtube.com') ||
          parsed.hostname.includes('youtu.be') ||
          parsed.hostname.includes('loom.com')
        );
      } catch {
        return true;
      }
    });
    
    if (invalidUrls.length > 0) {
      setError('Please enter valid YouTube or Loom URLs');
      return;
    }
    
    addVideoMutation.mutate(validUrls);
  };

  const handleAddUrl = () => {
    setUrls([...urls, '']);
  };

  const handleRemoveUrl = (index: number) => {
    setUrls(urls.filter((_, i) => i !== index));
  };

  const handleUrlChange = (index: number, value: string) => {
    const newUrls = [...urls];
    newUrls[index] = value;
    setUrls(newUrls);
  };

  const handleClose = () => {
    if (!addVideoMutation.isPending && !showProcessing) {
      onClose();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="w-full max-w-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <AnimatePresence mode="wait">
          {showProcessing ? (
            <motion.div
              key="processing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="bg-white rounded-lg shadow-xl p-6"
            >
              <VideoProcessingSkeleton />
            </motion.div>
          ) : (
            <motion.div
              key="form"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="bg-white rounded-lg shadow-xl overflow-hidden"
            >
              <div className="p-4 border-b">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-semibold">Add Videos</h2>
                  <button
                    onClick={handleClose}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <span className="sr-only">Close</span>
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              <form onSubmit={handleSubmit} className="p-4">
                <div className="space-y-4">
                  {urls.map((url, index) => (
                    <div key={index} className="flex gap-2">
                      <input
                        type="url"
                        placeholder="Enter YouTube or Loom video URL"
                        value={url}
                        onChange={(e) => handleUrlChange(index, e.target.value)}
                        className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-base px-4 py-3"
                      />
                      {urls.length > 1 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveUrl(index)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      )}
                    </div>
                  ))}
                  <button
                    type="button"
                    onClick={handleAddUrl}
                    className="text-indigo-600 hover:text-indigo-700 text-sm font-medium"
                  >
                    + Add Another URL
                  </button>
                  {error && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-sm text-red-600"
                    >
                      {error}
                    </motion.div>
                  )}
                  <div className="flex justify-end space-x-3">
                    <button
                      type="button"
                      onClick={handleClose}
                      className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={addVideoMutation.isPending}
                      className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {addVideoMutation.isPending ? 'Adding...' : 'Add Videos'}
                    </button>
                  </div>
                </div>
              </form>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
}; 