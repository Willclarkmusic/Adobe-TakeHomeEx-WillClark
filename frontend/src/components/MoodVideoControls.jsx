import React, { useState } from 'react';
import MoodPopup from './MoodPopup';

/**
 * Video generation controls for mood board using Veo.
 * Only 1 video at a time, max 1 source image.
 */
function MoodVideoControls({ campaign, onGenerated, onSettingsSaved }) {
  const [showPopup, setShowPopup] = useState(false);
  const [selectedImages, setSelectedImages] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [selectedRatio, setSelectedRatio] = useState('16:9');
  const [duration, setDuration] = useState(6);
  const [isGenerating, setIsGenerating] = useState(false);
  const [errors, setErrors] = useState({});

  const handleGenerate = async () => {
    if (isGenerating) {
      alert('A video is already generating. Please wait.');
      return;
    }

    if (!prompt.trim()) {
      setErrors({ prompt: 'Prompt required' });
      return;
    }

    setIsGenerating(true);
    setErrors({});

    try {
      const response = await fetch('/api/moods/videos/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          campaign_id: campaign.id,
          prompt,
          source_images: selectedImages,
          ratio: selectedRatio,
          duration
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail);
      }

      const generatedVideo = await response.json();
      onGenerated(generatedVideo);

      // Save settings for regen functionality
      if (onSettingsSaved) {
        onSettingsSaved({
          prompt,
          source_images: selectedImages,
          ratio: selectedRatio,
          duration
        });
      }

      // Reset form
      setPrompt('');
      setSelectedImages([]);

    } catch (error) {
      setErrors({ submit: error.message });
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="border-4 border-black dark:border-white p-4 bg-purple-50 dark:bg-purple-900/20">
      <h3 className="text-lg font-bold uppercase mb-4">🎬 Video Generation (Veo)</h3>

      {/* Source Image (max 1) */}
      <div className="mb-4">
        <label className="block text-sm font-bold uppercase mb-2">
          Reference Image (Max 1) {selectedImages.length > 0 && '✓'}
        </label>
        <button
          onClick={() => setShowPopup(true)}
          className="brutalist-button bg-purple-400 dark:bg-purple-600"
        >
          📎 Select Image
        </button>
        {selectedImages.length > 0 && (
          <div className="flex gap-2 mt-2 flex-wrap">
            {selectedImages.map((img, i) => (
              <img
                key={i}
                src={img.startsWith('/') ? img : `/static/${img}`}
                className="h-16 w-16 object-cover border-2 border-black dark:border-white"
              />
            ))}
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
          placeholder="Describe the video motion, atmosphere... (e.g., 'smooth zoom into product with cinematic lighting and slow rotation')"
          disabled={isGenerating}
        />
        {errors.prompt && <div className="text-red-500 text-sm mt-1">{errors.prompt}</div>}
      </div>

      {/* Ratio & Duration */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm font-bold uppercase mb-2">Aspect Ratio</label>
          <select
            value={selectedRatio}
            onChange={(e) => setSelectedRatio(e.target.value)}
            className="brutalist-input w-full"
            disabled={isGenerating}
          >
            <option value="16:9">16:9 (Landscape)</option>
            <option value="9:16">9:16 (Portrait)</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-bold uppercase mb-2">Duration</label>
          <select
            value={duration}
            onChange={(e) => setDuration(parseInt(e.target.value))}
            className="brutalist-input w-full"
            disabled={isGenerating}
          >
            <option value={4}>4 seconds</option>
            <option value={6}>6 seconds</option>
            <option value={8}>8 seconds</option>
          </select>
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={isGenerating || !prompt.trim()}
        className="brutalist-button bg-purple-400 dark:bg-purple-600 w-full disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isGenerating ? (
          <span>⏳ Generating Video... (this may take 30-60s)</span>
        ) : (
          <span>🎬 Generate Video</span>
        )}
      </button>

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
          maxImages={1}  // Video limited to 1 reference image
        />
      )}
    </div>
  );
}

export default MoodVideoControls;
