import React, { useState, useEffect } from "react";
import PostCard from "../components/PostCard";
import PostGenerateForm from "../components/PostGenerateForm";
import Modal from "../components/Modal";

/**
 * Posts Page - Displays and manages AI-generated post creatives
 */
function PostsPage({ selectedCampaign }) {
  // ============ State Management ============
  const [posts, setPosts] = useState([]);
  const [loadingPosts, setLoadingPosts] = useState(false);
  const [showGenerateModal, setShowGenerateModal] = useState(false);

  // ============ Lifecycle Methods ============

  useEffect(() => {
    if (selectedCampaign) {
      fetchPosts(selectedCampaign.id);
    } else {
      setPosts([]);
    }
  }, [selectedCampaign]);

  // ============ Data Fetching Methods ============

  const fetchPosts = async (campaignId) => {
    try {
      setLoadingPosts(true);
      const response = await fetch(`/api/posts?campaign_id=${campaignId}`);
      if (!response.ok) {
        throw new Error("Failed to fetch posts");
      }
      const data = await response.json();
      setPosts(data);
    } catch (err) {
      console.error("Error fetching posts:", err);
      setPosts([]);
    } finally {
      setLoadingPosts(false);
    }
  };

  // ============ Post Management Methods ============

  const openGenerateModal = () => {
    setShowGenerateModal(true);
  };

  const closeGenerateModal = () => {
    setShowGenerateModal(false);
  };

  const handlePostGenerated = (newPost) => {
    setPosts((prev) => [newPost, ...prev]);
    closeGenerateModal();
  };

  const handleDeletePost = async (postId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this post? This action cannot be undone."
    );
    if (!confirmed) return;

    try {
      const response = await fetch(`/api/posts/${postId}`, {
        method: "DELETE"
      });
      if (!response.ok) {
        throw new Error("Failed to delete post");
      }
      setPosts((prev) => prev.filter((p) => p.id !== postId));
    } catch (err) {
      console.error("Error deleting post:", err);
      alert("Failed to delete post");
    }
  };

  // ============ Render Methods ============

  const renderEmptyState = () => {
    return (
      <div className="border-4 border-dashed border-black dark:border-white p-8 text-center bg-gray-50 dark:bg-gray-800">
        <p className="text-6xl mb-4">🎨</p>
        <p className="font-bold uppercase text-xl mb-2">No Posts Yet</p>
        <p className="font-mono text-sm text-gray-600 dark:text-gray-400 mb-4">
          Generate your first AI-powered social media post by clicking the button above.
        </p>
        <button
          onClick={openGenerateModal}
          className="brutalist-button bg-green-400 dark:bg-green-600"
        >
          🚀 Generate Your First Post
        </button>
      </div>
    );
  };

  const renderPostsList = () => {
    if (posts.length === 0) {
      return renderEmptyState();
    }

    return (
      <div className="space-y-6">
        {posts.map((post) => (
          <PostCard key={post.id} post={post} onDelete={handleDeletePost} />
        ))}
      </div>
    );
  };

  const renderGenerateModal = () => {
    return (
      <Modal
        isOpen={showGenerateModal}
        onClose={closeGenerateModal}
        title="Generate AI Post"
      >
        <PostGenerateForm
          campaignId={selectedCampaign?.id}
          onGenerate={handlePostGenerated}
          onCancel={closeGenerateModal}
        />
      </Modal>
    );
  };

  // ============ Main Render ============

  if (!selectedCampaign) {
    return (
      <div className="brutalist-card">
        <p className="font-mono text-lg uppercase">
          ← Select a campaign to view posts
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="brutalist-card">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-3xl font-bold uppercase">
              🎨 Generated Posts
            </h2>
            <p className="font-mono text-sm text-gray-600 dark:text-gray-400 mt-1">
              AI-powered social media content for "{selectedCampaign.name}"
            </p>
          </div>
          <button
            onClick={openGenerateModal}
            className="brutalist-button bg-green-400 dark:bg-green-600"
          >
            + Generate Post
          </button>
        </div>
      </div>

      {/* Posts List */}
      {loadingPosts ? (
        <div className="brutalist-card">
          <p className="font-mono text-lg uppercase">Loading posts...</p>
        </div>
      ) : (
        renderPostsList()
      )}

      {/* Generate Modal */}
      {renderGenerateModal()}
    </div>
  );
}

export default PostsPage;
