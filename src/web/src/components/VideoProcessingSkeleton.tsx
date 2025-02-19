import React from 'react';
import { motion } from 'framer-motion';
import { processingSteps } from '../types/video';

export const VideoProcessingSkeleton: React.FC = () => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="bg-white rounded-lg shadow-md overflow-hidden min-h-[400px] flex flex-col"
    >
      {/* Thumbnail skeleton */}
      <div className="aspect-video bg-gray-100 relative">
        <motion.div 
          animate={{ 
            opacity: [0.5, 1, 0.5],
            transition: {
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }
          }}
          className="absolute inset-0 bg-gradient-to-r from-gray-200 to-gray-300" 
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.7, 1, 0.7],
              transition: {
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }
            }}
            className="w-16 h-16 rounded-full bg-gray-300 flex items-center justify-center"
          >
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </motion.div>
        </div>
      </div>
      
      {/* Content skeleton */}
      <div className="p-4 space-y-4 flex-1">
        {/* Title skeleton */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="h-6 bg-gray-200 rounded w-3/4" 
        />
        
        {/* Description skeleton */}
        <div className="space-y-2">
          <motion.div 
            animate={{ 
              opacity: [0.5, 1, 0.5],
              transition: {
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }
            }}
            className="h-4 bg-gray-200 rounded w-full" 
          />
          <motion.div 
            animate={{ 
              opacity: [0.5, 1, 0.5],
              transition: {
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }
            }}
            className="h-4 bg-gray-200 rounded w-5/6" 
          />
        </div>
        
        {/* Processing steps skeleton */}
        <div className="mt-4 space-y-3">
          {processingSteps.map((step, index) => (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="flex items-center space-x-3"
            >
              <motion.div
                animate={{
                  scale: [1, 1.2, 1],
                  transition: {
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }
                }}
                className="w-4 h-4 rounded-full bg-gray-200 flex-shrink-0"
              />
              <motion.div 
                animate={{ 
                  opacity: [0.5, 1, 0.5],
                  transition: {
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                  }
                }}
                className="h-4 bg-gray-200 rounded w-1/3" 
              />
            </motion.div>
          ))}
        </div>
        
        {/* Progress bar skeleton */}
        <div className="mt-4">
          <div className="h-2 bg-gray-200 rounded-full w-full overflow-hidden">
            <motion.div
              initial={{ width: "0%" }}
              animate={{ 
                width: "100%",
                transition: {
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }
              }}
              className="h-full bg-indigo-500"
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default VideoProcessingSkeleton; 