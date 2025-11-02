import React, { useState } from 'react';

/**
 * Manual file upload control for mood board.
 * Supports drag & drop for images and videos.
 */
function MoodUploadControls({ campaign, onUploaded }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    for (const file of files) {
      await uploadFile(file);
    }
  };

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files);
    for (const file of files) {
      await uploadFile(file);
    }
  };

  const uploadFile = async (file) => {
    if (!file.type.startsWith('image/') && !file.type.startsWith('video/')) {
      alert('Only images and videos allowed');
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`/api/moods/upload?campaign_id=${campaign.id}`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
      }

      const uploadedMedia = await response.json();
      onUploaded(uploadedMedia);

    } catch (error) {
      alert(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="border-4 border-black dark:border-white p-4 bg-green-50 dark:bg-green-900/20">
      <h3 className="text-lg font-bold uppercase mb-4">📤 Manual Upload</h3>

      <input
        type="file"
        multiple
        accept="image/*,video/*"
        onChange={handleFileSelect}
        className="hidden"
        id="mood-upload"
      />

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !uploading && document.getElementById('mood-upload').click()}
        className={`
          border-4 border-dashed p-6 text-center cursor-pointer transition-colors
          ${isDragging
            ? 'border-green-500 bg-green-100 dark:bg-green-900'
            : 'border-black dark:border-white'
          }
          ${uploading ? 'opacity-50 pointer-events-none' : ''}
        `}
      >
        <div className="text-3xl mb-2">📤</div>
        <div className="font-mono text-sm">
          {uploading ? (
            <span className="font-bold">Uploading...</span>
          ) : isDragging ? (
            <span className="font-bold text-green-600 dark:text-green-400">Drop files here!</span>
          ) : (
            <span>Click or drag & drop images/videos</span>
          )}
        </div>
        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          Uploaded files will be marked as not AI-generated
        </div>
      </div>
    </div>
  );
}

export default MoodUploadControls;
