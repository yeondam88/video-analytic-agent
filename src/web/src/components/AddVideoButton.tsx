import React from 'react';

interface AddVideoButtonProps {
  onClick: () => void;
}

export const AddVideoButton: React.FC<AddVideoButtonProps> = ({ onClick }) => {
  return (
    <button
      onClick={onClick}
      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
    >
      Add Video
    </button>
  );
}; 