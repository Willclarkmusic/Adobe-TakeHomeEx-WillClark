import React, { useState } from "react";
import MoodPopup from "./MoodPopup";

/**
 * PostGenerateForm Component - Form for AI post generation
 * Allows user to select source images (products or mood board), enter prompt, and choose aspect ratios
 */
function PostGenerateForm({ campaignId, onGenerate, onCancel }) {
  const [selectedImages, setSelectedImages] = useState([]);
  const [showImagePopup, setShowImagePopup] = useState(false);

  const [formData, setFormData] = useState({
    prompt: "",
    aspect_ratios: ["1:1"] // Default to 1:1
  });

  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Validation
    if (selectedImages.length === 0) {
      setError("Please select at least one source image");
      return;
    }
    if (!formData.prompt.trim()) {
      setError("Please enter a generation prompt");
      return;
    }
    if (formData.aspect_ratios.length === 0) {
      setError("Please select at least one aspect ratio");
      return;
    }

    try {
      setGenerating(true);

      const response = await fetch("/api/posts/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          campaign_id: campaignId,
          source_images: selectedImages,  // Array of image paths
          prompt: formData.prompt,
          aspect_ratios: formData.aspect_ratios
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate post");
      }

      const generatedPost = await response.json();
      onGenerate(generatedPost);

      // Reset form
      setSelectedImages([]);
      setFormData({
        prompt: "",
        aspect_ratios: ["1:1"]
      });
    } catch (err) {
      console.error("Error generating post:", err);
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleAspectRatioToggle = (ratio) => {
    setFormData(prev => {
      const ratios = prev.aspect_ratios.includes(ratio)
        ? prev.aspect_ratios.filter(r => r !== ratio)
        : [...prev.aspect_ratios, ratio];
      return { ...prev, aspect_ratios: ratios };
    });
  };

  const handleImageSelection = (images) => {
    setSelectedImages(images);
    setShowImagePopup(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Image Selector */}
      <div>
        <label className="block text-lg font-bold uppercase mb-2">
          Source Images {selectedImages.length > 0 && `(${selectedImages.length} selected)`}
        </label>
        <button
          type="button"
          onClick={() => setShowImagePopup(true)}
          className="brutalist-button bg-purple-400 dark:bg-purple-600 mb-3"
          disabled={generating}
        >
          📸 Select Images (Products or Mood Board)
        </button>

        {/* Selected Images Preview */}
        {selectedImages.length > 0 && (
          <div className="border-3 border-black dark:border-white p-3 bg-gray-50 dark:bg-gray-800">
            <div className="text-sm font-bold uppercase mb-2">Selected Images:</div>
            <div className="flex flex-wrap gap-2">
              {selectedImages.map((imgPath, index) => (
                <div
                  key={index}
                  className="relative w-20 h-20 border-2 border-black dark:border-white overflow-hidden"
                >
                  <img
                    src={imgPath.startsWith('/static/') ? imgPath : `/static/${imgPath}`}
                    alt={`Selected ${index + 1}`}
                    className="w-full h-full object-cover"
                  />
                  <button
                    type="button"
                    onClick={() => setSelectedImages(selectedImages.filter((_, i) => i !== index))}
                    className="absolute top-0 right-0 bg-red-500 text-white text-xs px-1 font-bold hover:bg-red-700"
                    disabled={generating}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
            <div className="text-xs font-mono text-gray-600 dark:text-gray-400 mt-2">
              {selectedImages.length === 1
                ? "📷 Single image: Will use image transformation (img2img)"
                : `🎨 ${selectedImages.length} images: Will create composition/blend`}
            </div>
          </div>
        )}
      </div>

      {/* Prompt Textarea */}
      <div>
        <label className="block text-lg font-bold uppercase mb-2">
          Generation Prompt
        </label>
        <textarea
          value={formData.prompt}
          onChange={(e) => setFormData(prev => ({ ...prev, prompt: e.target.value }))}
          placeholder="E.g., Create an engaging post highlighting the eco-friendly features and summer vibes..."
          className="brutalist-input w-full min-h-[120px] resize-y"
          disabled={generating}
        />
        <p className="text-sm font-mono text-gray-600 dark:text-gray-400 mt-2">
          Describe the tone, style, or specific features you want to highlight in the post.
        </p>
      </div>

      {/* Aspect Ratio Checkboxes */}
      <div>
        <label className="block text-lg font-bold uppercase mb-3">
          Aspect Ratios
        </label>
        <div className="space-y-2">
          <label className="flex items-center space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.aspect_ratios.includes("1:1")}
              onChange={() => handleAspectRatioToggle("1:1")}
              className="w-5 h-5 border-2 border-black dark:border-white"
              disabled={generating}
            />
            <span className="font-mono">
              <strong>1:1</strong> - Instagram Square (1080x1080)
            </span>
          </label>
          <label className="flex items-center space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.aspect_ratios.includes("16:9")}
              onChange={() => handleAspectRatioToggle("16:9")}
              className="w-5 h-5 border-2 border-black dark:border-white"
              disabled={generating}
            />
            <span className="font-mono">
              <strong>16:9</strong> - Landscape/YouTube (1920x1080)
            </span>
          </label>
          <label className="flex items-center space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.aspect_ratios.includes("9:16")}
              onChange={() => handleAspectRatioToggle("9:16")}
              className="w-5 h-5 border-2 border-black dark:border-white"
              disabled={generating}
            />
            <span className="font-mono">
              <strong>9:16</strong> - Story/Vertical (1080x1920)
            </span>
          </label>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="brutalist-card bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-200">
          <p className="font-mono text-sm">❌ {error}</p>
        </div>
      )}

      {/* Loading State */}
      {generating && (
        <div className="brutalist-card bg-blue-50 dark:bg-blue-900/20">
          <p className="font-mono text-lg uppercase">
            🤖 Generating post... This may take 10-20 seconds.
          </p>
          <p className="font-mono text-sm mt-2 text-gray-600 dark:text-gray-400">
            AI is writing copy and compositing images for {formData.aspect_ratios.length} aspect ratio(s)...
          </p>
          <p className="font-mono text-xs mt-2 text-gray-500 dark:text-gray-500">
            {selectedImages.length === 1
              ? "Using image transformation (img2img)"
              : `Creating composition from ${selectedImages.length} images`}
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          type="submit"
          disabled={generating}
          className="brutalist-button bg-green-400 dark:bg-green-600 flex-1"
        >
          {generating ? "Generating..." : "🚀 Generate Post"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={generating}
          className="brutalist-button bg-gray-300 dark:bg-gray-700"
        >
          Cancel
        </button>
      </div>

      {/* Image Selection Popup */}
      {showImagePopup && (
        <MoodPopup
          campaignId={campaignId}
          selectedImages={selectedImages}
          onCancel={() => setShowImagePopup(false)}
          onSelect={handleImageSelection}
          apiEndpoint="/api/posts/available-images"  // Use posts endpoint instead of moods
          maxImages={null}  // No limit on number of images
          title="Select Source Images"
          description="Choose images from products or mood board to generate your post"
        />
      )}
    </form>
  );
}

export default PostGenerateForm;
