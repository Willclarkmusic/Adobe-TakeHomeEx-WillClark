import React, { useState, useEffect } from 'react';
import MoodImageGenerateModal from '../components/MoodImageGenerateModal';
import MoodVideoGenerateModal from '../components/MoodVideoGenerateModal';
import MoodUploadControls from '../components/MoodUploadControls';
import MoodMasonryGallery from '../components/MoodMasonryGallery';

/**
 * Mood Board Page - Main page for AI-powered mood board generation.
 *
 * Features:
 * - Image generation (Gemini 2.5 Flash Image)
 * - Video generation (Veo)
 * - Manual uploads (drag & drop)
 * - Masonry gallery display
 * - Regen functionality with saved settings
 *
 * Props:
 * - selectedCampaign: Campaign object from header selector
 */
function MoodBoardPage({ selectedCampaign }) {
  const [moodMedia, setMoodMedia] = useState([]);
  const [showImageModal, setShowImageModal] = useState(false);
  const [showVideoModal, setShowVideoModal] = useState(false);
  const [loading, setLoading] = useState(false);

  // Track last generation settings for regen functionality
  const [lastImageSettings, setLastImageSettings] = useState(null);
  const [lastVideoSettings, setLastVideoSettings] = useState(null);

  useEffect(() => {
    if (selectedCampaign) {
      fetchMoodMedia(selectedCampaign.id);
    }
  }, [selectedCampaign]);

  const fetchMoodMedia = async (campaignId) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/moods?campaign_id=${campaignId}`);
      const data = await res.json();
      setMoodMedia(data);
    } catch (error) {
      console.error('Failed to fetch mood media:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMediaGenerated = (newMedia) => {
    // Add new media to top
    if (Array.isArray(newMedia)) {
      setMoodMedia(prev => [...newMedia, ...prev]);
    } else {
      setMoodMedia(prev => [newMedia, ...prev]);
    }
  };

  const handleMediaDeleted = (mediaId) => {
    setMoodMedia(prev => prev.filter(m => m.id !== mediaId));
  };

  const handleRegenImage = async () => {
    if (!lastImageSettings) {
      alert('No previous image generation settings found. Use Image Controls first.');
      return;
    }

    try {
      const response = await fetch('/api/moods/images/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          campaign_id: selectedCampaign.id,
          prompt: lastImageSettings.prompt,
          source_images: lastImageSettings.source_images,
          ratios: lastImageSettings.ratios
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail);
      }

      const generatedMedia = await response.json();
      handleMediaGenerated(generatedMedia);
    } catch (error) {
      alert(`Regen failed: ${error.message}`);
    }
  };

  const handleRegenVideo = async () => {
    if (!lastVideoSettings) {
      alert('No previous video generation settings found. Use Video Controls first.');
      return;
    }

    try {
      const response = await fetch('/api/moods/videos/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          campaign_id: selectedCampaign.id,
          prompt: lastVideoSettings.prompt,
          source_images: lastVideoSettings.source_images,
          ratio: lastVideoSettings.ratio,
          duration: lastVideoSettings.duration
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail);
      }

      const generatedVideo = await response.json();
      handleMediaGenerated(generatedVideo);
    } catch (error) {
      alert(`Regen failed: ${error.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-6">
        <h1 className="text-4xl font-bold uppercase mb-4 border-b-4 border-black dark:border-white pb-4">
          🎨 Mood Board
          {selectedCampaign && (
            <span className="text-xl ml-4 text-gray-600 dark:text-gray-400">
              {selectedCampaign.name}
            </span>
          )}
        </h1>

        {/* Controls Bar - 4 Generation Buttons + Upload + Refresh */}
        {selectedCampaign && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
            {/* Left: 4 Generation Buttons */}
            <div className="border-4 border-black dark:border-white p-4 bg-purple-50 dark:bg-purple-900/20">
              <h3 className="text-sm font-bold uppercase mb-3">AI Generation</h3>
              <div className="grid grid-cols-2 gap-2">
                {/* Image Controls */}
                <button
                  onClick={() => setShowImageModal(true)}
                  className="brutalist-button bg-blue-400 dark:bg-blue-600 text-sm"
                >
                  🖼️ Image Controls
                </button>

                {/* Regen Image */}
                <button
                  onClick={handleRegenImage}
                  disabled={!lastImageSettings}
                  className="brutalist-button bg-cyan-400 dark:bg-cyan-600 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  🔄 Regen Image
                </button>

                {/* Video Controls */}
                <button
                  onClick={() => setShowVideoModal(true)}
                  className="brutalist-button bg-purple-400 dark:bg-purple-600 text-sm"
                >
                  🎬 Video Controls
                </button>

                {/* Regen Video */}
                <button
                  onClick={handleRegenVideo}
                  disabled={!lastVideoSettings}
                  className="brutalist-button bg-pink-400 dark:bg-pink-600 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  🔄 Regen Vid
                </button>
              </div>
            </div>

            {/* Right: Upload Controls */}
            <MoodUploadControls
              campaign={selectedCampaign}
              onUploaded={handleMediaGenerated}
            />
          </div>
        )}

        {/* Refresh Button */}
        {selectedCampaign && (
          <div className="mb-4">
            <button
              onClick={() => fetchMoodMedia(selectedCampaign.id)}
              disabled={loading}
              className="brutalist-button bg-green-400 dark:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              🔄 Refresh Gallery
            </button>
          </div>
        )}

        {/* Stats */}
        {selectedCampaign && (
          <div className="mt-4 p-3 border-2 border-black dark:border-white bg-gray-50 dark:bg-gray-800">
            <div className="flex gap-6 text-sm font-mono">
              <span>
                <strong>Total:</strong> {moodMedia.length}
              </span>
              <span>
                <strong>Images:</strong> {moodMedia.filter(m => m.media_type === 'image').length}
              </span>
              <span>
                <strong>Videos:</strong> {moodMedia.filter(m => m.media_type === 'video').length}
              </span>
              <span>
                <strong>AI Generated:</strong> {moodMedia.filter(m => m.is_generated).length}
              </span>
              <span>
                <strong>Uploaded:</strong> {moodMedia.filter(m => !m.is_generated).length}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Masonry Gallery */}
      {selectedCampaign && (
        <>
          {loading ? (
            <div className="text-center py-20">
              <p className="text-xl font-bold">Loading...</p>
            </div>
          ) : (
            <MoodMasonryGallery
              moodMedia={moodMedia}
              onDelete={handleMediaDeleted}
              onRefresh={() => fetchMoodMedia(selectedCampaign.id)}
            />
          )}
        </>
      )}

      {/* No Campaign Selected */}
      {!selectedCampaign && (
        <div className="text-center py-20 border-4 border-dashed border-black dark:border-white">
          <p className="text-2xl font-bold mb-2">No campaign selected</p>
          <p className="text-gray-600 dark:text-gray-400">
            Select a campaign from the header to start building mood boards
          </p>
        </div>
      )}

      {/* Image Generation Modal */}
      {showImageModal && selectedCampaign && (
        <MoodImageGenerateModal
          campaign={selectedCampaign}
          onClose={() => setShowImageModal(false)}
          onMediaGenerated={handleMediaGenerated}
          onSettingsSaved={setLastImageSettings}
        />
      )}

      {/* Video Generation Modal */}
      {showVideoModal && selectedCampaign && (
        <MoodVideoGenerateModal
          campaign={selectedCampaign}
          onClose={() => setShowVideoModal(false)}
          onMediaGenerated={handleMediaGenerated}
          onSettingsSaved={setLastVideoSettings}
        />
      )}
    </div>
  );
}

export default MoodBoardPage;
