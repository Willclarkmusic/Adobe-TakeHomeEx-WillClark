import React, { useState } from 'react';
import MoodPopup from './MoodPopup';

/**
 * Image generation controls for mood board.
 * Supports queue management (max 5 images generating).
 */
function MoodImageControls({ campaign, onGenerated, onSettingsSaved }) {
  const [showPopup, setShowPopup] = useState(false);
  const [selectedImages, setSelectedImages] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [selectedRatios, setSelectedRatios] = useState(['1:1']);
  const [generatingQueue, setGeneratingQueue] = useState([]);
  const [errors, setErrors] = useState({});

  const RATIO_OPTIONS = ['1:1', '3:4', '4:3', '9:16', '16:9'];

  const toggleRatio = (ratio) => {
    if (selectedRatios.includes(ratio)) {
      setSelectedRatios(prev => prev.filter(r => r !== ratio));
    } else {
      if (selectedRatios.length >= 3) {
        setErrors({ ratios: 'Maximum 3 ratios allowed' });
        return;
      }
      setSelectedRatios(prev => [...prev, ratio]);
      setErrors(prev => ({ ...prev, ratios: undefined }));
    }
  };

  const handleGenerate = async () => {
    if (generatingQueue.length >= 5) {
      alert('Maximum 5 images can be generating at once. Please wait.');
      return;
    }

    if (!prompt.trim()) {
      setErrors({ prompt: 'Prompt required' });
      return;
    }

    if (selectedRatios.length === 0) {
      setErrors({ ratios: 'Select at least one ratio' });
      return;
    }

    // Add to queue
    const queueItems = selectedRatios.map(ratio => ({ ratio, status: 'generating' }));
    setGeneratingQueue(prev => [...prev, ...queueItems]);
    setErrors({});

    try {
      const response = await fetch('/api/moods/images/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          campaign_id: campaign.id,
          prompt,
          source_images: selectedImages,
          ratios: selectedRatios
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail);
      }

      const generatedMedia = await response.json();
      onGenerated(generatedMedia);

      // Save settings for regen functionality
      if (onSettingsSaved) {
        onSettingsSaved({
          prompt,
          source_images: selectedImages,
          ratios: selectedRatios
        });
      }

      // Clear queue items
      setGeneratingQueue(prev => prev.filter(item => !selectedRatios.includes(item.ratio)));

      // Reset form
      setPrompt('');
      setSelectedRatios(['1:1']);
      setSelectedImages([]);

    } catch (error) {
      setErrors({ submit: error.message });
      setGeneratingQueue(prev => prev.filter(item => !selectedRatios.includes(item.ratio)));
    }
  };

  const handleRegenerate = () => {
    handleGenerate();  // Reuse current settings
  };

  const canGenerate = generatingQueue.length < 5 && prompt.trim() && selectedRatios.length > 0;

  return (
    <div className="border-4 border-black dark:border-white p-4 bg-blue-50 dark:bg-blue-900/20">
      <h3 className="text-lg font-bold uppercase mb-4">🖼️ Image Generation</h3>

      {/* Source Images Selection */}
      <div className="mb-4">
        <label className="block text-sm font-bold uppercase mb-2">
          Source Images ({selectedImages.length} selected)
        </label>
        <button
          onClick={() => setShowPopup(true)}
          className="brutalist-button bg-purple-400 dark:bg-purple-600"
        >
          📎 Select Images
        </button>
        {selectedImages.length > 0 && (
          <div className="flex gap-2 mt-2 flex-wrap">
            {selectedImages.slice(0, 5).map((img, i) => (
              <img
                key={i}
                src={img.startsWith('/') ? img : `/static/${img}`}
                className="h-16 w-16 object-cover border-2 border-black dark:border-white"
              />
            ))}
            {selectedImages.length > 5 && (
              <div className="h-16 w-16 border-2 border-black dark:border-white flex items-center justify-center bg-gray-200 dark:bg-gray-700 text-xs font-bold">
                +{selectedImages.length - 5}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Prompt */}
      <div className="mb-4">
        <label className="block text-sm font-bold uppercase mb-2">Prompt *</label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="brutalist-input w-full min-h-[80px]"
          placeholder="Describe the mood, atmosphere, style... (e.g., 'vibrant summer vibes with bold colors and natural lighting')"
        />
        {errors.prompt && <div className="text-red-500 text-sm mt-1">{errors.prompt}</div>}
      </div>

      {/* Aspect Ratios */}
      <div className="mb-4">
        <label className="block text-sm font-bold uppercase mb-2">
          Aspect Ratios (Select up to 3)
        </label>
        <div className="flex gap-2 flex-wrap">
          {RATIO_OPTIONS.map(ratio => (
            <label key={ratio} className="flex items-center gap-2 cursor-pointer px-3 py-2 border-2 border-black dark:border-white bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700">
              <input
                type="checkbox"
                checked={selectedRatios.includes(ratio)}
                onChange={() => toggleRatio(ratio)}
                className="w-4 h-4"
              />
              <span className="font-mono text-sm font-bold">{ratio}</span>
            </label>
          ))}
        </div>
        {errors.ratios && <div className="text-red-500 text-sm mt-1">{errors.ratios}</div>}
      </div>

      {/* Queue Status */}
      {generatingQueue.length > 0 && (
        <div className="mb-4 p-3 border-2 border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20">
          <p className="font-mono text-sm">
            ⏳ Generating {generatingQueue.length}/5 images...
          </p>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={handleGenerate}
          disabled={!canGenerate}
          className="brutalist-button bg-green-400 dark:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          ✨ Generate ({selectedRatios.length} image{selectedRatios.length !== 1 ? 's' : ''})
        </button>
        <button
          onClick={handleRegenerate}
          disabled={!canGenerate}
          className="brutalist-button bg-blue-400 dark:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          🔄 Regenerate
        </button>
      </div>

      {errors.submit && (
        <div className="mt-4 p-3 border-4 border-red-500 bg-red-50 dark:bg-red-900 text-red-700 dark:text-red-200">
          <p className="font-mono text-sm">{errors.submit}</p>
        </div>
      )}

      {/* MoodPopup */}
      {showPopup && (
        <MoodPopup
          campaignId={campaign.id}
          selectedImages={selectedImages}
          onSelect={(images) => {
            setSelectedImages(images);
            setShowPopup(false);
          }}
          onCancel={() => setShowPopup(false)}
          maxSizeMB={17}
        />
      )}
    </div>
  );
}

export default MoodImageControls;
