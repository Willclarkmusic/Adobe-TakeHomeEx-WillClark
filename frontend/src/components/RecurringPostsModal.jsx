import React, { useState, useEffect } from 'react';

/**
 * RecurringPostsModal - Schedule recurring posts with rotation
 *
 * Features:
 * - Multi-select posts
 * - Frequency configuration (repeat count, interval in days)
 * - Order selection: Random or Sequential
 * - If Sequential: Reorder with up/down arrows
 * - Platform selection checkboxes
 */
function RecurringPostsModal({ campaign, selectedPlatforms, onClose, onPostScheduled }) {
  const [posts, setPosts] = useState([]);
  const [loadingPosts, setLoadingPosts] = useState(false);
  const [selectedPostIds, setSelectedPostIds] = useState([]);
  const [repeat, setRepeat] = useState(4); // Number of times to repeat
  const [daysInterval, setDaysInterval] = useState(7); // Days between posts
  const [startDateTime, setStartDateTime] = useState('');
  const [order, setOrder] = useState('sequential'); // 'sequential' or 'random'
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

  const togglePost = (postId) => {
    if (selectedPostIds.includes(postId)) {
      setSelectedPostIds(selectedPostIds.filter(id => id !== postId));
    } else {
      setSelectedPostIds([...selectedPostIds, postId]);
    }
  };

  const movePostUp = (index) => {
    if (index === 0) return;
    const newOrder = [...selectedPostIds];
    [newOrder[index - 1], newOrder[index]] = [newOrder[index], newOrder[index - 1]];
    setSelectedPostIds(newOrder);
  };

  const movePostDown = (index) => {
    if (index === selectedPostIds.length - 1) return;
    const newOrder = [...selectedPostIds];
    [newOrder[index], newOrder[index + 1]] = [newOrder[index + 1], newOrder[index]];
    setSelectedPostIds(newOrder);
  };

  const togglePlatform = (platform) => {
    if (selectedPostPlatforms.includes(platform)) {
      setSelectedPostPlatforms(selectedPostPlatforms.filter(p => p !== platform));
    } else {
      setSelectedPostPlatforms([...selectedPostPlatforms, platform]);
    }
  };

  const handleStartRecurring = async () => {
    // Validation
    if (selectedPostIds.length === 0) {
      setError('Please select at least one post');
      return;
    }

    if (!startDateTime) {
      setError('Please select a start date and time');
      return;
    }

    if (repeat < 1 || repeat > 10) {
      setError('Repeat count must be between 1 and 10');
      return;
    }

    if (daysInterval < 2) {
      setError('Days interval must be at least 2 days (Ayrshare limitation)');
      return;
    }

    if (selectedPostPlatforms.length === 0) {
      setError('Please select at least one platform');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      // For now, we'll use the first selected post for the recurring schedule
      // In a more advanced implementation, you could create multiple recurring schedules
      const firstPostId = selectedPostIds[0];

      const response = await fetch('/api/deploy/schedule-post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          post_id: firstPostId,
          campaign_id: campaign.id,
          schedule_type: 'recurring',
          platforms: selectedPostPlatforms,
          schedule_time: new Date(startDateTime).toISOString(),
          recurring_config: {
            repeat: repeat,
            days: daysInterval,
            order: order,
            post_ids: selectedPostIds
          }
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to schedule recurring posts');
      }

      const scheduledPost = await response.json();
      onPostScheduled(scheduledPost);
    } catch (err) {
      setError(err.message);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div
        className="bg-white dark:bg-gray-800 border-4 border-black dark:border-white max-w-5xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="border-b-4 border-black dark:border-white p-4 bg-purple-100 dark:bg-purple-900">
          <h2 className="text-2xl font-bold uppercase">🔁 Recurring Posts</h2>
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
              Select Posts * (Choose posts to rotate)
            </label>
            {loadingPosts ? (
              <div className="text-sm font-mono">Loading posts...</div>
            ) : posts.length === 0 ? (
              <div className="text-sm font-mono text-red-600 dark:text-red-400">
                No posts available. Create posts first.
              </div>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto border-2 border-black dark:border-white p-2">
                {posts.map((post) => (
                  <label
                    key={post.id}
                    className={`block border-2 border-black dark:border-white p-2 cursor-pointer ${
                      selectedPostIds.includes(post.id)
                        ? 'bg-purple-200 dark:bg-purple-800'
                        : 'bg-gray-100 dark:bg-gray-700'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedPostIds.includes(post.id)}
                      onChange={() => togglePost(post.id)}
                      className="mr-2"
                      disabled={isSubmitting}
                    />
                    <span className="font-bold">{post.headline}</span>
                    <span className="text-sm ml-2 text-gray-600 dark:text-gray-400">
                      | {post.body_text.substring(0, 50)}...
                    </span>
                  </label>
                ))}
              </div>
            )}
            <div className="text-xs font-mono mt-1 text-gray-600 dark:text-gray-400">
              {selectedPostIds.length} post(s) selected
            </div>
          </div>

          {/* Frequency Configuration */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold uppercase mb-2">
                Repeat Count * (1-10)
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={repeat}
                onChange={(e) => setRepeat(parseInt(e.target.value) || 1)}
                className="brutalist-input w-full"
                disabled={isSubmitting}
              />
              <div className="text-xs font-mono mt-1 text-gray-600 dark:text-gray-400">
                How many times to repeat
              </div>
            </div>

            <div>
              <label className="block text-sm font-bold uppercase mb-2">
                Interval (Days) * (min: 2)
              </label>
              <input
                type="number"
                min="2"
                value={daysInterval}
                onChange={(e) => setDaysInterval(parseInt(e.target.value) || 2)}
                className="brutalist-input w-full"
                disabled={isSubmitting}
              />
              <div className="text-xs font-mono mt-1 text-gray-600 dark:text-gray-400">
                Days between each post
              </div>
            </div>
          </div>

          {/* Start Date/Time */}
          <div>
            <label className="block text-sm font-bold uppercase mb-2">
              Start Date & Time *
            </label>
            <input
              type="datetime-local"
              value={startDateTime}
              onChange={(e) => setStartDateTime(e.target.value)}
              className="brutalist-input w-full"
              disabled={isSubmitting}
            />
          </div>

          {/* Order Selection */}
          <div>
            <label className="block text-sm font-bold uppercase mb-2">
              Post Order *
            </label>
            <div className="flex gap-4">
              <label className={`border-2 border-black dark:border-white p-3 cursor-pointer flex-1 ${
                order === 'sequential' ? 'bg-purple-200 dark:bg-purple-800' : 'bg-gray-100 dark:bg-gray-700'
              }`}>
                <input
                  type="radio"
                  value="sequential"
                  checked={order === 'sequential'}
                  onChange={(e) => setOrder(e.target.value)}
                  className="mr-2"
                  disabled={isSubmitting}
                />
                <span className="font-bold">📋 Sequential (in order)</span>
              </label>
              <label className={`border-2 border-black dark:border-white p-3 cursor-pointer flex-1 ${
                order === 'random' ? 'bg-purple-200 dark:bg-purple-800' : 'bg-gray-100 dark:bg-gray-700'
              }`}>
                <input
                  type="radio"
                  value="random"
                  checked={order === 'random'}
                  onChange={(e) => setOrder(e.target.value)}
                  className="mr-2"
                  disabled={isSubmitting}
                />
                <span className="font-bold">🎲 Random</span>
              </label>
            </div>
          </div>

          {/* Sequential Reordering */}
          {order === 'sequential' && selectedPostIds.length > 0 && (
            <div className="border-3 border-purple-500 dark:border-purple-400 p-4 bg-purple-50 dark:bg-purple-900/20">
              <div className="font-bold text-sm uppercase mb-2">Post Order (drag to reorder):</div>
              <div className="space-y-2">
                {selectedPostIds.map((postId, index) => {
                  const post = posts.find(p => p.id === postId);
                  if (!post) return null;
                  return (
                    <div
                      key={postId}
                      className="flex items-center gap-2 border-2 border-black dark:border-white p-2 bg-white dark:bg-gray-800"
                    >
                      <span className="font-bold text-sm w-6">{index + 1}.</span>
                      <span className="flex-1 font-mono text-sm truncate">{post.headline}</span>
                      <div className="flex gap-1">
                        <button
                          onClick={() => movePostUp(index)}
                          disabled={index === 0 || isSubmitting}
                          className="brutalist-button-sm bg-gray-300 dark:bg-gray-600 disabled:opacity-30"
                        >
                          ▲
                        </button>
                        <button
                          onClick={() => movePostDown(index)}
                          disabled={index === selectedPostIds.length - 1 || isSubmitting}
                          className="brutalist-button-sm bg-gray-300 dark:bg-gray-600 disabled:opacity-30"
                        >
                          ▼
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

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
              onClick={handleStartRecurring}
              disabled={
                isSubmitting ||
                selectedPostIds.length === 0 ||
                !startDateTime ||
                selectedPostPlatforms.length === 0
              }
              className="brutalist-button bg-purple-400 dark:bg-purple-600 flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? '⏳ Creating...' : '🔁 Start Recurring Posts'}
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

export default RecurringPostsModal;
