import React, { useState, useEffect } from 'react';

/**
 * Reusable image selector popup for mood board generation.
 *
 * Displays products and mood images for selection with size limit tracking.
 */
function MoodPopup({
  campaignId,
  onSelect,
  onCancel,
  maxSizeMB = 17,
  maxImages = null,  // null = unlimited, or specify max count
  selectedImages: initialSelected = []
}) {
  const [products, setProducts] = useState([]);
  const [moodImages, setMoodImages] = useState([]);
  const [selectedImages, setSelectedImages] = useState(initialSelected);
  const [totalSizeMB, setTotalSizeMB] = useState(0);

  useEffect(() => {
    fetchAvailableImages();
  }, [campaignId]);

  useEffect(() => {
    calculateTotalSize();
  }, [selectedImages]);

  const fetchAvailableImages = async () => {
    try {
      const res = await fetch(`/api/moods/available-images?campaign_id=${campaignId}`);
      const data = await res.json();
      setProducts(data.products || []);
      setMoodImages(data.mood_images || []);
    } catch (error) {
      console.error('Failed to fetch available images:', error);
    }
  };

  const calculateTotalSize = () => {
    // Estimate ~500KB per image (conservative)
    const estimatedSizeMB = selectedImages.length * 0.5;
    setTotalSizeMB(estimatedSizeMB);
  };

  const toggleImage = (imagePath) => {
    if (selectedImages.includes(imagePath)) {
      setSelectedImages(prev => prev.filter(p => p !== imagePath));
    } else {
      if (maxImages && selectedImages.length >= maxImages) {
        alert(`Maximum ${maxImages} images allowed`);
        return;
      }
      setSelectedImages(prev => [...prev, imagePath]);
    }
  };

  const handleConfirm = () => {
    if (totalSizeMB > maxSizeMB) {
      alert(`Total size (~${totalSizeMB.toFixed(1)} MB) exceeds ${maxSizeMB} MB limit. Please reduce selection.`);
      return;
    }
    onSelect(selectedImages);
  };

  const isOverLimit = totalSizeMB > maxSizeMB;
  const selectedCount = selectedImages.length;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-900 border-4 border-black dark:border-white max-w-4xl w-full max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="p-4 border-b-4 border-black dark:border-white bg-gray-50 dark:bg-gray-800">
          <h2 className="font-bold text-xl uppercase mb-2">Select Source Images</h2>
          <div className="flex gap-4 text-sm font-mono">
            <span className="font-bold">{selectedCount} selected</span>
            <span className={isOverLimit ? 'text-red-500 font-bold' : ''}>
              ~{totalSizeMB.toFixed(1)} / {maxSizeMB} MB
            </span>
            {maxImages && <span>Max: {maxImages}</span>}
          </div>
          {isOverLimit && (
            <div className="mt-2 text-red-500 font-bold text-sm border-2 border-red-500 bg-red-50 dark:bg-red-900 p-2">
              ⚠️ Too many images! Reduce selection to stay under {maxSizeMB} MB limit.
            </div>
          )}
        </div>

        {/* Scrollable Grid */}
        <div className="flex-1 overflow-y-auto p-4">
          {/* Products Section */}
          {products.length > 0 && (
            <div className="mb-6">
              <h3 className="font-bold uppercase mb-3 text-sm">📦 Products</h3>
              <div className="grid grid-cols-3 md:grid-cols-4 gap-3">
                {products.map(product => (
                  <div
                    key={product.id}
                    onClick={() => toggleImage(product.image_path)}
                    className={`
                      relative border-4 cursor-pointer transition-all hover:scale-105
                      ${selectedImages.includes(product.image_path)
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900 shadow-lg'
                        : 'border-black dark:border-white'
                      }
                    `}
                  >
                    <img
                      src={product.image_path}
                      alt={product.name}
                      className="w-full h-32 object-cover"
                    />
                    {selectedImages.includes(product.image_path) && (
                      <div className="absolute top-1 right-1 bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold shadow-lg">
                        ✓
                      </div>
                    )}
                    <div className="p-1 text-xs font-mono truncate bg-white dark:bg-gray-800">
                      {product.name}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Mood Images Section */}
          {moodImages.length > 0 && (
            <div>
              <h3 className="font-bold uppercase mb-3 text-sm">🎨 Mood Board Images</h3>
              <div className="grid grid-cols-3 md:grid-cols-4 gap-3">
                {moodImages.map(mood => (
                  <div
                    key={mood.id}
                    onClick={() => toggleImage(mood.file_path)}
                    className={`
                      relative border-4 cursor-pointer transition-all hover:scale-105
                      ${selectedImages.includes(mood.file_path)
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900 shadow-lg'
                        : 'border-black dark:border-white'
                      }
                    `}
                  >
                    <img
                      src={`/static/${mood.file_path}`}
                      className="w-full h-32 object-cover"
                    />
                    {selectedImages.includes(mood.file_path) && (
                      <div className="absolute top-1 right-1 bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold shadow-lg">
                        ✓
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Empty State */}
          {products.length === 0 && moodImages.length === 0 && (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg">No images available</p>
              <p className="text-sm">Add products or upload images to the mood board first</p>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="p-4 border-t-4 border-black dark:border-white bg-gray-50 dark:bg-gray-800 flex gap-3">
          <button
            onClick={handleConfirm}
            disabled={isOverLimit || selectedImages.length === 0}
            className="flex-1 brutalist-button bg-green-400 dark:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ✓ Select ({selectedCount})
          </button>
          <button
            onClick={onCancel}
            className="flex-1 brutalist-button bg-gray-300 dark:bg-gray-700"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

export default MoodPopup;
