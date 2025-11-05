import React, { useState, useEffect } from 'react';

/**
 * SchedulePostModal - Schedule a single post for immediate or future posting
 *
 * Features:
 * - Select a post from campaign
 * - Choose date/time for scheduling
 * - Select which platforms to post to (from selected campaign platforms)
 * - "Post Now" button - Posts immediately (~10 seconds)
 * - "Schedule" button - Schedules for selected date/time
 */
function SchedulePostModal({ campaign, selectedPlatforms, onClose, onPostScheduled }) {
  const [posts, setPosts] = useState([]);
  const [loadingPosts, setLoadingPosts] = useState(false);
  const [selectedPostId, setSelectedPostId] = useState('');
  const [scheduleDateTime, setScheduleDateTime] = useState('');
  const [selectedPostPlatforms, setSelectedPostPlatforms] = useState([...selectedPlatforms]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchPosts();
  }, [campaign.id]);

  const fetchPosts = async () => {
    try {
      setLoadingPosts(true);
      const response = await fetch(`/api/posts?campaign_id=${campaign.id}`);
      if (!response.ok) throw new Error('Failed to fetch posts');
      const data = await response.json();
      setPosts(data);
    } catch (err) {
      console.error('Error fetching posts:', err);
      setPosts([]);
    } finally {
      setLoadingPosts(false);
    }
  };

  const togglePlatform = (platform) => {
    if (selectedPostPlatforms.includes(platform)) {
      setSelectedPostPlatforms(selectedPostPlatforms.filter(p => p !== platform));
    } else {
      setSelectedPostPlatforms([...selectedPostPlatforms, platform]);
    }
  };

  const handlePostNow = async () => {
    if (!selectedPostId) {
      setError('Please select a post');
      return;
    }

    if (selectedPostPlatforms.length === 0) {
      setError('Please select at least one platform');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const response = await fetch('/api/deploy/schedule-post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          post_id: selectedPostId,
          campaign_id: campaign.id,
          schedule_type: 'immediate',
          platforms: selectedPostPlatforms,
          schedule_time: null,
          recurring_config: null
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to schedule post');
      }

      const scheduledPost = await response.json();
      onPostScheduled(scheduledPost);
    } catch (err) {
      setError(err.message);
      setIsSubmitting(false);
    }
  };

  const handleSchedule = async () => {
    if (!selectedPostId) {
      setError('Please select a post');
      return;
    }

    if (!scheduleDateTime) {
      setError('Please select a date and time');
      return;
    }

    if (selectedPostPlatforms.length === 0) {
      setError('Please select at least one platform');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const response = await fetch('/api/deploy/schedule-post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          post_id: selectedPostId,
          campaign_id: campaign.id,
          schedule_type: 'scheduled',
          platforms: selectedPostPlatforms,
          schedule_time: new Date(scheduleDateTime).toISOString(),
          recurring_config: null
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to schedule post');
      }

      const scheduledPost = await response.json();
      onPostScheduled(scheduledPost);
    } catch (err) {
      setError(err.message);
      setIsSubmitting(false);
    }
  };

  const selectedPost = posts.find(p => p.id === selectedPostId);

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div
        className="bg-white dark:bg-gray-800 border-4 border-black dark:border-white max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="border-b-4 border-black dark:border-white p-4 bg-blue-100 dark:bg-blue-900">
          <h2 className="text-2xl font-bold uppercase">📌 Schedule Post</h2>
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-2xl font-bold hover:text-red-500"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Post Selection */}
          <div>
            <label className="block text-sm font-bold uppercase mb-2">
              Select Post *
            </label>
            {loadingPosts ? (
              <div className="text-sm font-mono">Loading posts...</div>
            ) : posts.length === 0 ? (
              <div className="text-sm font-mono text-red-600 dark:text-red-400">
                No posts available. Create posts first.
              </div>
            ) : (
              <select
                value={selectedPostId}
                onChange={(e) => setSelectedPostId(e.target.value)}
                className="brutalist-input w-full"
                disabled={isSubmitting}
              >
                <option value="">-- Select a post --</option>
                {posts.map((post) => (
                  <option key={post.id} value={post.id}>
                    {post.headline} | {post.body_text.substring(0, 50)}...
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Post Preview */}
          {selectedPost && (
            <div className="border-3 border-black dark:border-white p-4 bg-gray-50 dark:bg-gray-700">
              <div className="font-bold uppercase text-sm mb-2">Post Preview:</div>
              <div className="space-y-2">
                <div>
                  <span className="font-bold">Headline:</span> {selectedPost.headline}
                </div>
                <div>
                  <span className="font-bold">Body:</span> {selectedPost.body_text}
                </div>
                <div>
                  <span className="font-bold">Caption:</span> {selectedPost.caption}
                </div>
                {selectedPost.image_1_1 && (
                  <img
                    src={`/static/${selectedPost.image_1_1}`}
                    alt="Post preview"
                    className="w-32 h-32 object-cover border-2 border-black dark:border-white"
                  />
                )}
              </div>
            </div>
          )}

          {/* Date/Time Picker */}
          <div>
            <label className="block text-sm font-bold uppercase mb-2">
              Schedule Date & Time (Optional - for scheduled posts)
            </label>
            <input
              type="datetime-local"
              value={scheduleDateTime}
              onChange={(e) => setScheduleDateTime(e.target.value)}
              className="brutalist-input w-full"
              disabled={isSubmitting}
            />
          </div>

          {/* Platform Selection */}
          <div>
            <label className="block text-sm font-bold uppercase mb-2">
              Platforms to Post To *
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {selectedPlatforms.map((platform) => (
                <label
                  key={platform}
                  className={`border-2 border-black dark:border-white p-2 cursor-pointer ${
                    selectedPostPlatforms.includes(platform)
                      ? 'bg-green-200 dark:bg-green-800'
                      : 'bg-gray-100 dark:bg-gray-700'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedPostPlatforms.includes(platform)}
                    onChange={() => togglePlatform(platform)}
                    className="mr-2"
                    disabled={isSubmitting}
                  />
                  <span className="font-bold text-sm uppercase">{platform}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 border-2 border-red-500 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 font-mono text-sm">
              ❌ {error}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={handlePostNow}
              disabled={isSubmitting || !selectedPostId || selectedPostPlatforms.length === 0}
              className="brutalist-button bg-green-400 dark:bg-green-600 flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? '⏳ Posting...' : '⚡ Post Now'}
            </button>
            <button
              onClick={handleSchedule}
              disabled={isSubmitting || !selectedPostId || !scheduleDateTime || selectedPostPlatforms.length === 0}
              className="brutalist-button bg-blue-400 dark:bg-blue-600 flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? '⏳ Scheduling...' : '📅 Schedule'}
            </button>
            <button
              onClick={onClose}
              disabled={isSubmitting}
              className="brutalist-button bg-gray-400 dark:bg-gray-600"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SchedulePostModal;
