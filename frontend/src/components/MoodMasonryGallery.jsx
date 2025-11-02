import React, { useState } from 'react';
import Masonry from 'react-masonry-css';
import MoodMediaModal from './MoodMediaModal';

/**
 * Masonry gallery for displaying mood board media.
 * Supports shuffle, delete, and fullscreen view.
 */
function MoodMasonryGallery({ moodMedia, onDelete, onRefresh }) {
  const [selectedMedia, setSelectedMedia] = useState(null);
  const [displayMedia, setDisplayMedia] = useState(() => shuffleArray([...moodMedia]));

  // Update display when moodMedia changes (new items at top)
  React.useEffect(() => {
    setDisplayMedia(moodMedia);
  }, [moodMedia]);

  const handleShuffle = () => {
    setDisplayMedia(prev => shuffleArray([...prev]));
  };

  const handleDelete = async (mediaId) => {
    if (!confirm('Delete this media? This cannot be undone.')) return;

    try {
      const response = await fetch(`/api/moods/${mediaId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        onDelete(mediaId);
      } else {
        const error = await response.json();
        alert(`Delete failed: ${error.detail}`);
      }
    } catch (error) {
      alert('Delete failed');
    }
  };

  const breakpointColumns = {
    default: 4,
    1536: 3,
    1024: 2,
    640: 1
  };

  return (
    <div className="max-w-7xl mx-auto relative">
      {/* Empty State */}
      {displayMedia.length === 0 && (
        <div className="text-center py-20 border-4 border-dashed border-black dark:border-white">
          <p className="text-2xl font-bold mb-2">🎨 No mood media yet</p>
          <p className="text-gray-600 dark:text-gray-400">
            Generate images/videos or upload files to get started
          </p>
        </div>
      )}

      {/* Masonry Gallery */}
      {displayMedia.length > 0 && (
        <Masonry
          breakpointCols={breakpointColumns}
          className="flex -ml-4 w-auto"
          columnClassName="pl-4 bg-clip-padding"
        >
          {displayMedia.map(media => (
            <div
              key={media.id}
              className="mb-4 relative group cursor-pointer"
              onClick={() => setSelectedMedia(media)}
            >
              {media.media_type === 'image' ? (
                <img
                  src={`/static/${media.file_path}`}
                  alt="Mood"
                  className="w-full border-4 border-black dark:border-white transition-transform hover:scale-[1.02] hover:shadow-lg"
                />
              ) : (
                <div className="relative">
                  <video
                    src={`/static/${media.file_path}`}
                    className="w-full border-4 border-black dark:border-white"
                    preload="metadata"
                  />
                  {/* Play icon overlay */}
                  <div className="absolute inset-0 flex items-center justify-center bg-black/30 pointer-events-none">
                    <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-lg">
                      <span className="text-3xl ml-1">▶️</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Delete button */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(media.id);
                }}
                className="absolute top-2 right-2 px-3 py-1 bg-red-500 text-white font-bold text-xs border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] opacity-0 group-hover:opacity-100 transition-opacity hover:shadow-none"
              >
                ✕
              </button>

              {/* Generated/Uploaded indicator */}
              {!media.is_generated && (
                <div className="absolute bottom-2 left-2 px-2 py-1 bg-blue-500 text-white text-xs font-bold border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                  📤 Uploaded
                </div>
              )}

              {/* Aspect ratio badge */}
              {media.aspect_ratio && (
                <div className="absolute bottom-2 right-2 px-2 py-1 bg-purple-500 text-white text-xs font-bold border-2 border-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                  {media.aspect_ratio}
                </div>
              )}
            </div>
          ))}
        </Masonry>
      )}

      {/* Shuffle button (bottom-right corner) */}
      {displayMedia.length > 0 && (
        <button
          onClick={handleShuffle}
          className="fixed bottom-8 right-8 brutalist-button bg-yellow-400 dark:bg-yellow-600 shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-shadow z-40"
        >
          🔀 Shuffle
        </button>
      )}

      {/* Fullscreen Modal */}
      {selectedMedia && (
        <MoodMediaModal
          media={selectedMedia}
          onClose={() => setSelectedMedia(null)}
        />
      )}
    </div>
  );
}

/**
 * Fisher-Yates shuffle algorithm
 */
function shuffleArray(array) {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

export default MoodMasonryGallery;
