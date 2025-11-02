import React from 'react';

/**
 * Platform icon/emoji mapping
 */
const PLATFORM_ICONS = {
  instagram: '📷',
  facebook: '👍',
  twitter: '🐦',
  x: '🐦',
  linkedin: '💼',
  tiktok: '🎵',
  youtube: '▶️',
  pinterest: '📌',
  reddit: '👽',
  telegram: '✈️',
  threads: '🧵',
  bluesky: '🦋',
  snapchat: '👻',
  gbp: '🗺️'
};

/**
 * ScheduledPostCard - Display a scheduled social media post
 *
 * Shows:
 * - Post preview (image + headline)
 * - Schedule type and date/time
 * - Target platforms
 * - Status (pending/posted/failed)
 * - Delete button to cancel scheduled post
 */
function ScheduledPostCard({ scheduledPost, onDelete }) {
  const post = scheduledPost.post;
  const platforms = JSON.parse(scheduledPost.platforms || '[]');
  const recurringConfig = scheduledPost.recurring_config
    ? JSON.parse(scheduledPost.recurring_config)
    : null;

  // Format schedule time
  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  // Schedule type badge
  const getTypeBadge = () => {
    switch (scheduledPost.schedule_type) {
      case 'immediate':
        return <span className="px-2 py-1 bg-green-400 dark:bg-green-600 text-xs font-bold border-2 border-black dark:border-white">⚡ IMMEDIATE</span>;
      case 'scheduled':
        return <span className="px-2 py-1 bg-blue-400 dark:bg-blue-600 text-xs font-bold border-2 border-black dark:border-white">📅 SCHEDULED</span>;
      case 'recurring':
        return <span className="px-2 py-1 bg-purple-400 dark:bg-purple-600 text-xs font-bold border-2 border-black dark:border-white">🔁 RECURRING</span>;
      default:
        return null;
    }
  };

  // Status badge
  const getStatusBadge = () => {
    switch (scheduledPost.status) {
      case 'pending':
        return <span className="px-2 py-1 bg-yellow-300 dark:bg-yellow-600 text-xs font-bold border-2 border-black dark:border-white">⏳ PENDING</span>;
      case 'posted':
        return <span className="px-2 py-1 bg-green-300 dark:bg-green-600 text-xs font-bold border-2 border-black dark:border-white">✅ POSTED</span>;
      case 'failed':
        return <span className="px-2 py-1 bg-red-300 dark:bg-red-600 text-xs font-bold border-2 border-black dark:border-white">❌ FAILED</span>;
      case 'cancelled':
        return <span className="px-2 py-1 bg-gray-300 dark:bg-gray-600 text-xs font-bold border-2 border-black dark:border-white">🚫 CANCELLED</span>;
      default:
        return null;
    }
  };

  // Get post image
  const getPostImage = () => {
    if (post?.image_1_1) return `/static/${post.image_1_1}`;
    if (post?.image_16_9) return `/static/${post.image_16_9}`;
    if (post?.image_9_16) return `/static/${post.image_9_16}`;
    return null;
  };

  const handleDelete = () => {
    if (confirm('Are you sure you want to cancel this scheduled post?')) {
      onDelete(scheduledPost.id);
    }
  };

  return (
    <div className="border-4 border-black dark:border-white bg-white dark:bg-gray-800 overflow-hidden">
      {/* Post Image */}
      {getPostImage() && (
        <div className="aspect-square border-b-4 border-black dark:border-white overflow-hidden">
          <img
            src={getPostImage()}
            alt={post?.headline || 'Post'}
            className="w-full h-full object-cover"
          />
        </div>
      )}

      {/* Content */}
      <div className="p-3 space-y-2">
        {/* Headline */}
        <div className="font-bold text-sm line-clamp-2 min-h-[2.5rem]">
          {post?.headline || 'No headline'}
        </div>

        {/* Type & Status Badges */}
        <div className="flex gap-2 flex-wrap">
          {getTypeBadge()}
          {getStatusBadge()}
        </div>

        {/* Schedule Info */}
        <div className="text-xs font-mono space-y-1">
          {scheduledPost.schedule_type === 'immediate' && (
            <div>⚡ Posted immediately</div>
          )}
          {scheduledPost.schedule_type === 'scheduled' && (
            <div>📅 {formatDateTime(scheduledPost.schedule_time)}</div>
          )}
          {scheduledPost.schedule_type === 'recurring' && recurringConfig && (
            <>
              <div>🔁 Starts: {formatDateTime(scheduledPost.schedule_time)}</div>
              <div>📊 {recurringConfig.repeat}x every {recurringConfig.days} days</div>
              <div>📋 Order: {recurringConfig.order}</div>
            </>
          )}
        </div>

        {/* Platforms */}
        <div className="border-t-2 border-black dark:border-white pt-2">
          <div className="text-xs font-bold uppercase mb-1">Platforms:</div>
          <div className="flex gap-1 flex-wrap">
            {platforms.map((platform) => {
              const icon = PLATFORM_ICONS[platform.toLowerCase()] || '📱';
              return (
                <span
                  key={platform}
                  className="px-1 py-0.5 bg-gray-200 dark:bg-gray-700 text-xs border border-black dark:border-white"
                  title={platform}
                >
                  {icon}
                </span>
              );
            })}
          </div>
        </div>

        {/* Error Message */}
        {scheduledPost.error_message && (
          <div className="text-xs font-mono text-red-600 dark:text-red-400 border-2 border-red-500 bg-red-50 dark:bg-red-900/20 p-2">
            ❌ {scheduledPost.error_message}
          </div>
        )}

        {/* Delete Button */}
        <button
          onClick={handleDelete}
          className="brutalist-button bg-red-400 dark:bg-red-600 w-full text-sm py-2"
        >
          🗑️ Cancel
        </button>
      </div>
    </div>
  );
}

export default ScheduledPostCard;
