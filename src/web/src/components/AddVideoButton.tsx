import React, { useState } from 'react';
import { AddVideoModal } from './AddVideoModal';

export const AddVideoButton: React.FC = () => {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
      >
        Add Video
      </button>

      {showModal && <AddVideoModal onClose={() => setShowModal(false)} />}
    </>
  );
}; 