import React from "react";
import { NavLink } from "react-router-dom";

/**
 * Header Component - Contains app title, theme toggle, campaign selector, and navigation
 * Presentational component that receives all data and callbacks via props
 */
function Header({
  isDark,
  onToggleTheme,
  campaigns,
  selectedCampaign,
  onCampaignChange,
  onNewCampaign,
  onEditCampaign,
  onDeleteCampaign,
  loading,
  error,
}) {
  // ============ Render Methods - Title & Theme ============

  const renderTitle = () => {
    return (
      <header className="mb-12">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-5xl font-bold uppercase tracking-tight">
            Creative Automation Hub
          </h1>
          {renderThemeToggle()}
        </div>
        <div className="h-1 bg-black dark:bg-white"></div>
      </header>
    );
  };

  const renderThemeToggle = () => {
    return (
      <button
        onClick={onToggleTheme}
        className="brutalist-button"
        aria-label="Toggle theme"
      >
        {isDark ? "☀️ LIGHT" : "🌙 DARK"}
      </button>
    );
  };

  // ============ Render Methods - Campaign Selector ============

  const renderCampaignSelector = () => {
    if (loading) {
      return (
        <div className="brutalist-card mb-6">
          <p className="font-mono text-lg uppercase">Loading campaigns...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="brutalist-card bg-red-100 dark:bg-red-900 mb-6">
          <p className="font-mono text-red-600 dark:text-red-200">
            Error: {error}
          </p>
        </div>
      );
    }

    return (
      <div className="brutalist-card mb-6">
        <div className="flex justify-between items-center mb-2">
          <label className="block text-xl font-bold uppercase">Campaign:</label>
        </div>

        <div className="flex gap-2 flex-wrap mb-2">
          <select
            value={selectedCampaign?.id || ""}
            onChange={onCampaignChange}
            className="brutalist-select flex-1"
          >
            {campaigns.map((campaign) => (
              <option key={campaign.id} value={campaign.id}>
                {campaign.name}
              </option>
            ))}
          </select>

          <button
            onClick={onNewCampaign}
            className="brutalist-button bg-green-400 dark:bg-green-600 text-sm"
          >
            + New Campaign
          </button>

          {selectedCampaign && (
            <>
              <button
                onClick={onEditCampaign}
                className="brutalist-button bg-yellow-300 dark:bg-yellow-600"
              >
                ✏️ Edit
              </button>
              <button
                onClick={onDeleteCampaign}
                className="brutalist-button bg-red-500 text-white"
              >
                🗑️ Delete
              </button>
            </>
          )}
        </div>
        <div className="">{renderNavigation()}</div>
      </div>
    );
  };

  // ============ Render Methods - Navigation ============

  const renderNavigation = () => {
    if (!selectedCampaign) return null;

    return (
      <nav className="flex flex-wrap gap-2 py-2 justify-center w-full">
        <NavLink
          to="/campaign"
          className={({ isActive }) =>
            `px-6 py-3 border-2 border-black dark:border-white font-bold uppercase text-sm transition-colors ${
              isActive
                ? "bg-black dark:bg-white text-white dark:text-black"
                : "bg-white dark:bg-black text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-800"
            }`
          }
        >
          📋 Campaign
        </NavLink>
        <NavLink
          to="/posts"
          className={({ isActive }) =>
            `px-6 py-3 border-2 border-black dark:border-white font-bold uppercase text-sm transition-colors ${
              isActive
                ? "bg-black dark:bg-white text-white dark:text-black"
                : "bg-white dark:bg-black text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-800"
            }`
          }
        >
          🎨 Posts
        </NavLink>
        <NavLink
          to="/moodboard"
          className={({ isActive }) =>
            `px-6 py-3 border-2 border-black dark:border-white font-bold uppercase text-sm transition-colors ${
              isActive
                ? "bg-black dark:bg-white text-white dark:text-black"
                : "bg-white dark:bg-black text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-800"
            }`
          }
        >
          🖼️ Mood Board
        </NavLink>
        <NavLink
          to="/metrics"
          className={({ isActive }) =>
            `px-6 py-3 border-2 border-black dark:border-white font-bold uppercase text-sm transition-colors ${
              isActive
                ? "bg-black dark:bg-white text-white dark:text-black"
                : "bg-white dark:bg-black text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-800"
            }`
          }
        >
          📊 Metrics
        </NavLink>
      </nav>
    );
  };

  // ============ Main Render ============

  return (
    <>
      {renderTitle()}
      {renderCampaignSelector()}
    </>
  );
}

export default Header;
