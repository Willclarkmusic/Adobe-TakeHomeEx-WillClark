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
 * Common social media platforms
 */
const ALL_PLATFORMS = [
  { key: 'instagram', name: 'Instagram' },
  { key: 'facebook', name: 'Facebook' },
  { key: 'x', name: 'X (Twitter)' },
  { key: 'linkedin', name: 'LinkedIn' },
  { key: 'tiktok', name: 'TikTok' },
  { key: 'youtube', name: 'YouTube' },
  { key: 'pinterest', name: 'Pinterest' },
  { key: 'reddit', name: 'Reddit' },
  { key: 'threads', name: 'Threads' },
  { key: 'telegram', name: 'Telegram' }
];

/**
 * DeployCampaignSetup - Select platforms for this campaign
 *
 * Features:
 * - Multi-select checkboxes for each platform
 * - ⚠️ Warning badge for platforms not connected in accounts section
 * - Visual distinction for connected vs not connected platforms
 */
function DeployCampaignSetup({
  campaign,
  profiles,
  selectedPlatforms,
  onPlatformsChange
}) {
  // Get list of connected platform keys
  const connectedPlatformKeys = profiles.map(p => p.platform.toLowerCase());

  const togglePlatform = (platformKey) => {
    if (selectedPlatforms.includes(platformKey)) {
      onPlatformsChange(selectedPlatforms.filter(p => p !== platformKey));
    } else {
      onPlatformsChange([...selectedPlatforms, platformKey]);
    }
  };

  const selectAll = () => {
    onPlatformsChange(ALL_PLATFORMS.map(p => p.key));
  };

  const selectOnlyConnected = () => {
    onPlatformsChange(connectedPlatformKeys);
  };

  const clearAll = () => {
    onPlatformsChange([]);
  };

  return (
    <div className="border-4 border-black dark:border-white p-6 bg-white dark:bg-gray-800">
      <h2 className="text-2xl font-bold uppercase mb-4">🎯 Campaign Platforms</h2>

      <div className="mb-4">
        <p className="font-mono text-sm mb-2">
          Select which platforms to use for this campaign:
        </p>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={selectOnlyConnected}
            className="brutalist-button-sm bg-green-400 dark:bg-green-600"
          >
            ✓ Select Connected
          </button>
          <button
            onClick={selectAll}
            className="brutalist-button-sm bg-blue-400 dark:bg-blue-600"
          >
            Select All
          </button>
          <button
            onClick={clearAll}
            className="brutalist-button-sm bg-gray-400 dark:bg-gray-600"
          >
            Clear All
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
        {ALL_PLATFORMS.map((platform) => {
          const isConnected = connectedPlatformKeys.includes(platform.key);
          const isSelected = selectedPlatforms.includes(platform.key);
          const icon = PLATFORM_ICONS[platform.key] || '📱';

          return (
            <label
              key={platform.key}
              className={`border-3 border-black dark:border-white p-3 cursor-pointer transition-colors ${
                isSelected
                  ? isConnected
                    ? 'bg-green-200 dark:bg-green-800'
                    : 'bg-yellow-200 dark:bg-yellow-800'
                  : isConnected
                  ? 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600'
                  : 'bg-gray-50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-700/50'
              }`}
            >
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => togglePlatform(platform.key)}
                  className="w-4 h-4"
                />
                <span className="text-xl">{icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="font-bold text-sm uppercase truncate">
                    {platform.name}
                  </div>
                  {!isConnected && (
                    <div className="text-xs text-red-600 dark:text-red-400 font-bold">
                      ⚠️ Not Setup
                    </div>
                  )}
                </div>
              </div>
            </label>
          );
        })}
      </div>

      {selectedPlatforms.length > 0 && (
        <div className="mt-4 p-3 border-2 border-green-500 dark:border-green-400 bg-green-50 dark:bg-green-900/20">
          <div className="font-bold text-sm mb-1">
            ✓ Selected Platforms ({selectedPlatforms.length}):
          </div>
          <div className="flex gap-2 flex-wrap">
            {selectedPlatforms.map((key) => {
              const platform = ALL_PLATFORMS.find(p => p.key === key);
              const isConnected = connectedPlatformKeys.includes(key);
              const icon = PLATFORM_ICONS[key] || '📱';

              return (
                <span
                  key={key}
                  className={`px-2 py-1 border-2 border-black dark:border-white text-xs font-bold ${
                    isConnected
                      ? 'bg-green-300 dark:bg-green-700'
                      : 'bg-yellow-300 dark:bg-yellow-700'
                  }`}
                >
                  {icon} {platform?.name || key}
                  {!isConnected && ' ⚠️'}
                </span>
              );
            })}
          </div>
          {selectedPlatforms.some(key => !connectedPlatformKeys.includes(key)) && (
            <div className="mt-2 text-xs font-mono text-yellow-700 dark:text-yellow-300">
              ⚠️ Warning: Some selected platforms are not connected. Posts to these platforms will fail.
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default DeployCampaignSetup;
