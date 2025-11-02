import React, { useState, useEffect } from 'react';
import DeployAccountsSection from '../components/DeployAccountsSection';
import DeployCampaignSetup from '../components/DeployCampaignSetup';
import DeployScheduler from '../components/DeployScheduler';
import ScheduledPostCard from '../components/ScheduledPostCard';

/**
 * Deploy Page - Social media deployment and scheduling
 *
 * Sections:
 * 1. Accounts - Show connected social media accounts from Ayrshare
 * 2. Campaign Setup - Select platforms for this campaign
 * 3. Scheduler - Schedule posts (immediate, future, or recurring)
 * 4. Scheduled Posts Grid - Display all scheduled posts for this campaign
 */
function DeployPage({ selectedCampaign }) {
  const [profiles, setProfiles] = useState([]);
  const [loadingProfiles, setLoadingProfiles] = useState(false);
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [scheduledPosts, setScheduledPosts] = useState([]);
  const [loadingScheduledPosts, setLoadingScheduledPosts] = useState(false);

  // Fetch connected profiles on mount
  useEffect(() => {
    fetchProfiles();
  }, []);

  // Fetch scheduled posts when campaign changes
  useEffect(() => {
    if (selectedCampaign) {
      fetchScheduledPosts(selectedCampaign.id);
    } else {
      setScheduledPosts([]);
    }
  }, [selectedCampaign]);

  const fetchProfiles = async () => {
    try {
      setLoadingProfiles(true);
      const response = await fetch('/api/deploy/profiles');
      if (!response.ok) throw new Error('Failed to fetch profiles');
      const data = await response.json();
      setProfiles(data.profiles || []);
    } catch (err) {
      console.error('Error fetching profiles:', err);
      setProfiles([]);
    } finally {
      setLoadingProfiles(false);
    }
  };

  const fetchScheduledPosts = async (campaignId) => {
    try {
      setLoadingScheduledPosts(true);
      const response = await fetch(`/api/deploy/scheduled-posts?campaign_id=${campaignId}`);
      if (!response.ok) throw new Error('Failed to fetch scheduled posts');
      const data = await response.json();
      setScheduledPosts(data);
    } catch (err) {
      console.error('Error fetching scheduled posts:', err);
      setScheduledPosts([]);
    } finally {
      setLoadingScheduledPosts(false);
    }
  };

  const handlePostScheduled = (newScheduledPost) => {
    // Add new scheduled post to the list
    setScheduledPosts([newScheduledPost, ...scheduledPosts]);
  };

  const handlePostDeleted = async (scheduledPostId) => {
    try {
      const response = await fetch(`/api/deploy/scheduled-posts/${scheduledPostId}`, {
        method: 'DELETE'
      });

      if (!response.ok) throw new Error('Failed to delete scheduled post');

      // Remove from list
      setScheduledPosts(scheduledPosts.filter(sp => sp.id !== scheduledPostId));
    } catch (err) {
      console.error('Error deleting scheduled post:', err);
      alert(`Failed to delete: ${err.message}`);
    }
  };

  if (!selectedCampaign) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="border-4 border-black dark:border-white p-8 bg-gray-100 dark:bg-gray-800">
          <h2 className="text-2xl font-bold uppercase text-center">
            📱 Select a campaign to deploy
          </h2>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Page Header */}
      <div className="border-4 border-black dark:border-white p-6 bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-900 dark:to-purple-900">
        <h1 className="text-3xl font-bold uppercase">📱 Deploy to Social Media</h1>
        <p className="font-mono text-sm mt-2">
          Campaign: <span className="font-bold">{selectedCampaign.name}</span>
        </p>
      </div>

      {/* Section 1: Connected Accounts */}
      <DeployAccountsSection
        profiles={profiles}
        loading={loadingProfiles}
        onRefresh={fetchProfiles}
      />

      {/* Section 2: Campaign Platform Setup */}
      <DeployCampaignSetup
        campaign={selectedCampaign}
        profiles={profiles}
        selectedPlatforms={selectedPlatforms}
        onPlatformsChange={setSelectedPlatforms}
      />

      {/* Section 3: Scheduler */}
      <DeployScheduler
        campaign={selectedCampaign}
        selectedPlatforms={selectedPlatforms}
        onPostScheduled={handlePostScheduled}
      />

      {/* Section 4: Scheduled Posts Grid */}
      <div className="border-4 border-black dark:border-white p-6 bg-white dark:bg-gray-800">
        <h2 className="text-2xl font-bold uppercase mb-4">📅 Scheduled Posts</h2>

        {loadingScheduledPosts ? (
          <div className="text-center py-8">
            <div className="text-lg font-mono">Loading scheduled posts...</div>
          </div>
        ) : scheduledPosts.length === 0 ? (
          <div className="text-center py-8 border-2 border-dashed border-gray-300 dark:border-gray-600">
            <div className="text-lg font-mono text-gray-500 dark:text-gray-400">
              No scheduled posts yet. Use the scheduler above to create one.
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {scheduledPosts.map((scheduledPost) => (
              <ScheduledPostCard
                key={scheduledPost.id}
                scheduledPost={scheduledPost}
                onDelete={handlePostDeleted}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default DeployPage;
