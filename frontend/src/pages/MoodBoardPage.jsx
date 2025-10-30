import React from "react";

/**
 * Mood Board Page - Will display visual inspiration and assets
 * Currently placeholder for future implementation
 */
function MoodBoardPage({ selectedCampaign }) {
  if (!selectedCampaign) {
    return (
      <div className="brutalist-card">
        <p className="font-mono text-lg uppercase">
          ← Select a campaign to view mood board
        </p>
      </div>
    );
  }

  return (
    <div className="brutalist-card space-y-6">
      <h2 className="text-3xl font-bold uppercase border-b-4 border-black dark:border-white pb-4">
        🖼️ Mood Board
      </h2>
      <div className="space-y-4">
        <p className="font-mono text-lg">
          Coming soon: Visual inspiration board for "{selectedCampaign.name}"
        </p>
        <div className="border-4 border-dashed border-black dark:border-white p-8 text-center bg-gray-50 dark:bg-gray-800">
          <p className="text-6xl mb-4">🎨</p>
          <p className="font-bold uppercase text-xl mb-2">Mood Board Feature</p>
          <p className="font-mono text-sm text-gray-600 dark:text-gray-400">
            This will allow you to collect and organize visual inspiration,
            color palettes, and reference images for your campaign.
          </p>
        </div>
      </div>
    </div>
  );
}

export default MoodBoardPage;
