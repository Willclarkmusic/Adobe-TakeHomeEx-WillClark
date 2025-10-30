import React from "react";

/**
 * Metrics Page - Will display campaign performance analytics
 * Currently placeholder for future implementation
 */
function MetricsPage({ selectedCampaign }) {
  if (!selectedCampaign) {
    return (
      <div className="brutalist-card">
        <p className="font-mono text-lg uppercase">
          ← Select a campaign to view metrics
        </p>
      </div>
    );
  }

  return (
    <div className="brutalist-card space-y-6">
      <h2 className="text-3xl font-bold uppercase border-b-4 border-black dark:border-white pb-4">
        📊 Campaign Metrics
      </h2>
      <div className="space-y-4">
        <p className="font-mono text-lg">
          Coming soon: Performance analytics for "{selectedCampaign.name}"
        </p>
        <div className="border-4 border-dashed border-black dark:border-white p-8 text-center bg-gray-50 dark:bg-gray-800">
          <p className="text-6xl mb-4">📈</p>
          <p className="font-bold uppercase text-xl mb-2">Metrics & Analytics Feature</p>
          <p className="font-mono text-sm text-gray-600 dark:text-gray-400">
            This will display engagement metrics, reach, performance data,
            and ROI tracking for your campaign and generated posts.
          </p>
        </div>
      </div>
    </div>
  );
}

export default MetricsPage;
