import React from 'react';
import MoodImageControls from './MoodImageControls';

/**
 * Modal for image generation only.
 * Focused interface for generating mood board images.
 */
function MoodImageGenerateModal({ campaign, onClose, onMediaGenerated, onSettingsSaved }) {
  const handleGenerated = (media) => {
    onMediaGenerated(media);
    // Don't auto-close - let user generate multiple times
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 border-4 border-black dark:border-white max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="p-4 border-b-4 border-black dark:border-white flex justify-between items-center sticky top-0 bg-white dark:bg-gray-900 z-10">
          <h2 className="text-2xl font-bold uppercase">🖼️ Generate Images</h2>
          <button
            onClick={onClose}
            className="brutalist-button bg-red-400 hover:bg-red-500"
          >
            ✕ Close
          </button>
        </div>

        <div className="p-6">
          <MoodImageControls
            campaign={campaign}
            onGenerated={handleGenerated}
            onSettingsSaved={onSettingsSaved}
          />
        </div>
      </div>
    </div>
  );
}

export default MoodImageGenerateModal;
