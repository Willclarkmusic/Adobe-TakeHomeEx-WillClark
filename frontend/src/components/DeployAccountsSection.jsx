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
  gbp: '🗺️' // Google Business Profile
};

/**
 * DeployAccountsSection - Display connected social media accounts
 *
 * Shows all profiles/accounts connected in Ayrshare with:
 * - Platform icon
 * - Platform name
 * - Username/handle
 * - Active status
 */
function DeployAccountsSection({ profiles, loading, onRefresh }) {
  if (loading) {
    return (
      <div className="border-4 border-black dark:border-white p-6 bg-white dark:bg-gray-800">
        <h2 className="text-2xl font-bold uppercase mb-4">🔗 Connected Accounts</h2>
        <div className="text-center py-8">
          <div className="text-lg font-mono">Loading accounts...</div>
        </div>
      </div>
    );
  }

  if (profiles.length === 0) {
    return (
      <div className="border-4 border-black dark:border-white p-6 bg-white dark:bg-gray-800">
        <h2 className="text-2xl font-bold uppercase mb-4">🔗 Connected Accounts</h2>
        <div className="text-center py-8 border-2 border-dashed border-red-500 dark:border-red-400 bg-red-50 dark:bg-red-900/20">
          <div className="text-lg font-bold text-red-700 dark:text-red-300 mb-2">
            ⚠️ No accounts connected
          </div>
          <div className="text-sm font-mono text-red-600 dark:text-red-400 mb-4">
            Connect social media accounts in Ayrshare dashboard first
          </div>
          <a
            href="https://app.ayrshare.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="brutalist-button bg-red-400 dark:bg-red-600 inline-block"
          >
            Open Ayrshare Dashboard
          </a>
          <button
            onClick={onRefresh}
            className="brutalist-button bg-blue-400 dark:bg-blue-600 ml-2"
          >
            🔄 Refresh
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="border-4 border-black dark:border-white p-6 bg-white dark:bg-gray-800">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold uppercase">🔗 Connected Accounts</h2>
        <button
          onClick={onRefresh}
          className="brutalist-button-sm bg-blue-400 dark:bg-blue-600"
        >
          🔄 Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {profiles.map((profile) => {
          const icon = PLATFORM_ICONS[profile.platform.toLowerCase()] || '📱';
          const platformName = profile.platform.charAt(0).toUpperCase() + profile.platform.slice(1);

          return (
            <div
              key={profile.profile_key}
              className={`border-3 border-black dark:border-white p-3 ${
                profile.is_active
                  ? 'bg-green-100 dark:bg-green-900/30'
                  : 'bg-gray-100 dark:bg-gray-700/30'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-2xl">{icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="font-bold text-sm uppercase truncate">
                    {platformName}
                  </div>
                  {profile.username && (
                    <div className="text-xs font-mono truncate text-gray-600 dark:text-gray-400">
                      @{profile.username}
                    </div>
                  )}
                  {profile.display_name && !profile.username && (
                    <div className="text-xs font-mono truncate text-gray-600 dark:text-gray-400">
                      {profile.display_name}
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-1 mt-2">
                <div
                  className={`w-2 h-2 rounded-full ${
                    profile.is_active ? 'bg-green-500' : 'bg-gray-400'
                  }`}
                />
                <span className="text-xs font-mono">
                  {profile.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-4 p-3 border-2 border-blue-500 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/20 text-sm font-mono">
        <span className="font-bold">💡 Tip:</span> To add more accounts, visit{' '}
        <a
          href="https://app.ayrshare.com/"
          target="_blank"
          rel="noopener noreferrer"
          className="underline font-bold hover:text-blue-600 dark:hover:text-blue-300"
        >
          Ayrshare Dashboard
        </a>
        {' '}and connect your social media profiles.
      </div>
    </div>
  );
}

export default DeployAccountsSection;
