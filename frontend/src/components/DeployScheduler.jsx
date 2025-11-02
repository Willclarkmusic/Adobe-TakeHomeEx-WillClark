import React, { useState } from 'react';
import SchedulePostModal from './SchedulePostModal';
import RecurringPostsModal from './RecurringPostsModal';

/**
 * DeployScheduler - Schedule posts for social media
 *
 * Features:
 * - Display campaign start/end dates and running time
 * - "Schedule Post" button - Opens modal for single post scheduling
 * - "Recurring Posts" button - Opens modal for recurring post scheduling
 */
function DeployScheduler({ campaign, selectedPlatforms, onPostScheduled }) {
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [showRecurringModal, setShowRecurringModal] = useState(false);

  // Calculate campaign dates
  const startDate = campaign.start_date ? new Date(campaign.start_date) : null;
  const duration = campaign.duration || 0;
  const endDate = startDate && duration
    ? new Date(startDate.getTime() + duration * 24 * 60 * 60 * 1000)
    : null;

  // Calculate days remaining
  const today = new Date();
  const daysRemaining = endDate
    ? Math.ceil((endDate - today) / (1000 * 60 * 60 * 24))
    : null;

  return (
    <>
      <div className="border-4 border-black dark:border-white p-6 bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900 dark:to-pink-900">
        <h2 className="text-2xl font-bold uppercase mb-4">📅 Scheduler</h2>

        {/* Campaign Timeline */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="border-2 border-black dark:border-white p-3 bg-white dark:bg-gray-800">
            <div className="text-xs font-bold uppercase text-gray-600 dark:text-gray-400 mb-1">
              Start Date
            </div>
            <div className="text-lg font-bold font-mono">
              {startDate ? startDate.toLocaleDateString() : 'Not Set'}
            </div>
          </div>

          <div className="border-2 border-black dark:border-white p-3 bg-white dark:bg-gray-800">
            <div className="text-xs font-bold uppercase text-gray-600 dark:text-gray-400 mb-1">
              End Date
            </div>
            <div className="text-lg font-bold font-mono">
              {endDate ? endDate.toLocaleDateString() : 'Not Set'}
            </div>
          </div>

          <div className="border-2 border-black dark:border-white p-3 bg-white dark:bg-gray-800">
            <div className="text-xs font-bold uppercase text-gray-600 dark:text-gray-400 mb-1">
              Running Time
            </div>
            <div className="text-lg font-bold font-mono">
              {duration > 0 ? `${duration} days` : 'Not Set'}
            </div>
            {daysRemaining !== null && daysRemaining >= 0 && (
              <div className="text-xs text-green-600 dark:text-green-400 font-bold mt-1">
                {daysRemaining} days remaining
              </div>
            )}
            {daysRemaining !== null && daysRemaining < 0 && (
              <div className="text-xs text-red-600 dark:text-red-400 font-bold mt-1">
                Campaign ended
              </div>
            )}
          </div>
        </div>

        {/* Platform Selection Warning */}
        {selectedPlatforms.length === 0 && (
          <div className="mb-4 p-3 border-2 border-red-500 dark:border-red-400 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300">
            <span className="font-bold">⚠️ No platforms selected.</span> Please select platforms in the Campaign Platforms section above before scheduling posts.
          </div>
        )}

        {/* Scheduling Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => setShowScheduleModal(true)}
            disabled={selectedPlatforms.length === 0}
            className="brutalist-button bg-blue-400 dark:bg-blue-600 text-lg py-4 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            📌 Schedule Post
          </button>

          <button
            onClick={() => setShowRecurringModal(true)}
            disabled={selectedPlatforms.length === 0}
            className="brutalist-button bg-purple-400 dark:bg-purple-600 text-lg py-4 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            🔁 Recurring Posts
          </button>
        </div>

        <div className="mt-4 text-sm font-mono text-gray-700 dark:text-gray-300">
          <div>
            <span className="font-bold">📌 Schedule Post:</span> Post a specific post at a specific time, or post immediately.
          </div>
          <div className="mt-1">
            <span className="font-bold">🔁 Recurring Posts:</span> Schedule multiple posts to repeat automatically at regular intervals.
          </div>
        </div>
      </div>

      {/* Modals */}
      {showScheduleModal && (
        <SchedulePostModal
          campaign={campaign}
          selectedPlatforms={selectedPlatforms}
          onClose={() => setShowScheduleModal(false)}
          onPostScheduled={(scheduledPost) => {
            onPostScheduled(scheduledPost);
            setShowScheduleModal(false);
          }}
        />
      )}

      {showRecurringModal && (
        <RecurringPostsModal
          campaign={campaign}
          selectedPlatforms={selectedPlatforms}
          onClose={() => setShowRecurringModal(false)}
          onPostScheduled={(scheduledPost) => {
            onPostScheduled(scheduledPost);
            setShowRecurringModal(false);
          }}
        />
      )}
    </>
  );
}

export default DeployScheduler;
