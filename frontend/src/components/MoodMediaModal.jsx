import React, { useEffect } from 'react';

/**
 * Fullscreen modal for viewing mood media (images/videos).
 * Videos autoplay with controls. ESC key to close.
 */
function MoodMediaModal({ media, onClose }) {
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  if (!media) return null;

  return (
    <div
      className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="relative max-w-[90vw] max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute -top-12 right-0 text-white text-xl font-bold hover:text-red-500 transition-colors px-4 py-2 border-2 border-white"
        >
          ✕ Close
        </button>

        {/* Media */}
        {media.media_type === 'image' ? (
          <img
            src={`/static/${media.file_path}`}
            alt="Mood"
            className="max-w-full max-h-[90vh] border-4 border-white"
          />
        ) : (
          <video
            src={`/static/${media.file_path}`}
            controls
            autoPlay
            className="max-w-full max-h-[90vh] border-4 border-white"
          />
        )}

        {/* Info overlay */}
        <div className="absolute bottom-0 left-0 right-0 bg-black/80 text-white p-3 text-sm font-mono">
          <div className="flex justify-between items-center">
            <span>{media.aspect_ratio || 'Custom'}</span>
            <span>{media.is_generated ? '✨ AI Generated' : '📤 Uploaded'}</span>
          </div>
          {media.prompt && (
            <div className="mt-2 text-xs opacity-75 line-clamp-2">
              Prompt: {media.prompt}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default MoodMediaModal;
