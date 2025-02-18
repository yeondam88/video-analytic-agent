import React from 'react';
import { VideoStatus } from '../types/video';

interface ProcessingStatusProps {
  status: VideoStatus;
  progress: number;
  steps: string[];
}

export const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  status,
  progress,
  steps
}) => {
  const getStatusColor = (status: VideoStatus) => {
    switch (status) {
      case VideoStatus.FAILED:
        return 'text-red-500';
      case VideoStatus.COMPLETED:
        return 'text-green-500';
      default:
        return 'text-blue-500';
    }
  };

  return (
    <div className="bg-white shadow-lg rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Processing Status</h2>
      
      {/* Status Badge */}
      <div className="mb-4">
        <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(status)}`}>
          {status}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
        <div
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Steps List */}
      <div className="space-y-2">
        {steps.map((step, index) => (
          <div
            key={step}
            className="flex items-center text-sm"
          >
            <div className={`w-4 h-4 rounded-full mr-3 flex items-center justify-center ${
              index === steps.length - 1 ? 'bg-blue-500' : 'bg-green-500'
            }`}>
              <svg
                className="w-3 h-3 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <span className="text-gray-700">{step}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProcessingStatus; 