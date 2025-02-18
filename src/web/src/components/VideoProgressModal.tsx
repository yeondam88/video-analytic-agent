import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { VideoStatus } from '../types/video';
import { processingSteps } from '../types/video';

interface VideoProgressModalProps {
  video: {
    id: string;
    title: string | null;
    status: VideoStatus;
    progress: number;
    steps_completed?: string[];
    error?: string;
  };
  onClose: () => void;
}

export const VideoProgressModal: React.FC<VideoProgressModalProps> = ({ video, onClose }) => {
  const currentStep = processingSteps.findIndex(step => 
    video.steps_completed?.includes(step.id)
  );

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          transition={{ type: "spring", duration: 0.5 }}
          className="bg-white rounded-xl shadow-xl w-full max-w-lg m-4 overflow-hidden"
          onClick={e => e.stopPropagation()}
        >
          {/* Header */}
          <motion.div
            initial={{ y: -20 }}
            animate={{ y: 0 }}
            className="p-6 border-b"
          >
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">
                {video.title || 'Processing Video'}
              </h2>
              <button
                onClick={onClose}
                className="text-gray-500 hover:text-gray-700 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </motion.div>

          {/* Progress Content */}
          <div className="p-6">
            {/* Overall Progress */}
            <div className="mb-8">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Overall Progress</span>
                <span className="text-sm font-medium text-gray-900">{Math.round(video.progress)}%</span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${video.progress}%` }}
                  transition={{ duration: 0.5 }}
                  className="h-full bg-indigo-600 rounded-full"
                />
              </div>
            </div>

            {/* Processing Steps */}
            <div className="space-y-4">
              {processingSteps.map((step, index) => {
                const isCompleted = video.steps_completed?.includes(step.id);
                const isCurrent = video.steps_completed?.length === index;
                
                return (
                  <motion.div
                    key={step.id}
                    initial={{ x: -20, opacity: 0 }}
                    animate={{ x: 0, opacity: 1 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center space-x-4"
                  >
                    <motion.div
                      animate={{
                        scale: isCurrent ? [1, 1.1, 1] : 1,
                        backgroundColor: isCompleted ? '#4F46E5' : isCurrent ? '#818CF8' : '#E5E7EB'
                      }}
                      transition={{ repeat: isCurrent ? Infinity : 0, duration: 2 }}
                      className="w-8 h-8 rounded-full flex items-center justify-center"
                    >
                      {isCompleted ? (
                        <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      ) : isCurrent ? (
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                          className="w-5 h-5 border-2 border-white rounded-full border-t-transparent"
                        />
                      ) : (
                        <div className="w-2 h-2 bg-gray-400 rounded-full" />
                      )}
                    </motion.div>
                    <div className="flex-1">
                      <p className={`text-sm font-medium ${
                        isCompleted ? 'text-gray-900' : isCurrent ? 'text-indigo-600' : 'text-gray-500'
                      }`}>
                        {step.label}
                      </p>
                    </div>
                  </motion.div>
                );
              })}
            </div>

            {/* Error Message */}
            {video.error && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg"
              >
                <p className="text-sm text-red-600">{video.error}</p>
              </motion.div>
            )}
          </div>

          {/* Footer */}
          <motion.div
            initial={{ y: 20 }}
            animate={{ y: 0 }}
            className="p-6 border-t bg-gray-50"
          >
            <div className="flex justify-end">
              <button
                onClick={onClose}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
              >
                Close
              </button>
            </div>
          </motion.div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}; 