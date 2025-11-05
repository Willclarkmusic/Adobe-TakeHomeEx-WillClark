import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useTheme } from "./context/ThemeContext";
import Header from "./components/common/Header";
import Modal from "./components/Modal";
import CampaignForm, { CampaignFormJsonTab } from "./components/CampaignForm";
import CampaignPage from "./pages/CampaignPage";
import PostsPage from "./pages/PostsPage";
import MoodBoardPage from "./pages/MoodBoardPage";
import MetricsPage from "./pages/MetricsPage";
import DeployPage from "./pages/DeployPage";

/**
 * Main App component with router
 * Manages global state and renders routes
 */
function App() {
  const { isDark, toggleTheme } = useTheme();

  // ============ State Management ============
  const [campaigns, setCampaigns] = useState([]);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showCampaignModal, setShowCampaignModal] = useState(false);
  const [editingCampaign, setEditingCampaign] = useState(null);

  // ============ Lifecycle Methods ============

  useEffect(() => {
    fetchCampaigns();
  }, []);

  // ============ Data Fetching Methods ============

  const fetchCampaigns = async () => {
    try {
      setLoading(true);
      const data = await sendGetCampaignsRequest();
      handleCampaignsReceived(data);
    } catch (err) {
      handleFetchError(err, "campaigns");
    } finally {
      setLoading(false);
    }
  };

  const sendGetCampaignsRequest = async () => {
    const response = await fetch("/api/campaigns");
    if (!response.ok) {
      throw new Error("Failed to fetch campaigns");
    }
    return response.json();
  };

  const handleCampaignsReceived = (data) => {
    setCampaigns(data);
    if (data.length > 0 && !selectedCampaign) {
      setSelectedCampaign(data[0]);
    }
  };

  const handleFetchError = (err, resource) => {
    setError(err.message);
    console.error(`Error fetching ${resource}:`, err);
  };

  // ============ Campaign Management Methods ============

  const openNewCampaignModal = () => {
    setEditingCampaign(null);
    setShowCampaignModal(true);
  };

  const openEditCampaignModal = () => {
    setEditingCampaign(selectedCampaign);
    setShowCampaignModal(true);
  };

  const closeCampaignModal = () => {
    setShowCampaignModal(false);
    setEditingCampaign(null);
  };

  const handleCampaignSaved = (savedCampaign) => {
    if (editingCampaign) {
      updateCampaignInList(savedCampaign);
    } else {
      addCampaignToList(savedCampaign);
    }
    closeCampaignModal();
  };

  const updateCampaignInList = (updatedCampaign) => {
    setCampaigns((prev) =>
      prev.map((c) => (c.id === updatedCampaign.id ? updatedCampaign : c))
    );
    if (selectedCampaign?.id === updatedCampaign.id) {
      setSelectedCampaign(updatedCampaign);
    }
  };

  const addCampaignToList = (newCampaign) => {
    setCampaigns((prev) => [...prev, newCampaign]);
    setSelectedCampaign(newCampaign);
  };

  const handleCampaignChange = (e) => {
    const campaign = findCampaignById(e.target.value);
    setSelectedCampaign(campaign);
  };

  const findCampaignById = (id) => {
    return campaigns.find((c) => c.id === id);
  };

  const handleDeleteCampaign = async () => {
    if (!selectedCampaign) return;

    const confirmed = window.confirm(
      `⚠️ WARNING ⚠️\n\n` +
      `You are about to PERMANENTLY DELETE the campaign:\n` +
      `"${selectedCampaign.name}"\n\n` +
      `This will also delete ALL associated products and posts!\n\n` +
      `This action CANNOT be undone.\n\n` +
      `Are you absolutely sure?`
    );

    if (!confirmed) return;

    try {
      await sendDeleteCampaignRequest(selectedCampaign.id);
      removeCampaignFromList(selectedCampaign.id);
    } catch (err) {
      console.error("Error deleting campaign:", err);
      alert("Failed to delete campaign");
    }
  };

  const sendDeleteCampaignRequest = async (campaignId) => {
    const response = await fetch(`/api/campaigns/${campaignId}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      throw new Error("Failed to delete campaign");
    }
  };

  const removeCampaignFromList = (campaignId) => {
    const updatedCampaigns = campaigns.filter((c) => c.id !== campaignId);
    setCampaigns(updatedCampaigns);
    // Select first campaign if any remain
    setSelectedCampaign(updatedCampaigns.length > 0 ? updatedCampaigns[0] : null);
  };

  // ============ Render Methods - Modals ============

  const renderCampaignModal = () => {
    const renderJsonTab = () => {
      return (
        <CampaignFormJsonTab
          campaign={editingCampaign}
          onSave={handleCampaignSaved}
          onCancel={closeCampaignModal}
        />
      );
    };

    const renderManualTab = () => {
      return (
        <CampaignForm
          campaign={editingCampaign}
          onSave={handleCampaignSaved}
          onCancel={closeCampaignModal}
          onTabSwitch={(index) => {
            // Tab switch handled by modal
          }}
        />
      );
    };

    return (
      <Modal
        isOpen={showCampaignModal}
        onClose={closeCampaignModal}
        title={editingCampaign ? "Edit Campaign" : "New Campaign"}
        tabs={[
          { label: "Manual", content: renderManualTab() },
          { label: "JSON", content: renderJsonTab() },
        ]}
      />
    );
  };

  // ============ Main Render ============

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-white dark:bg-black text-black dark:text-white transition-colors">
        <div className="max-w-7xl mx-auto px-4 py-8">

          {/* Header: Title, Theme Toggle, Campaign Selector, Navigation */}
          <Header
            isDark={isDark}
            onToggleTheme={toggleTheme}
            campaigns={campaigns}
            selectedCampaign={selectedCampaign}
            onCampaignChange={handleCampaignChange}
            onNewCampaign={openNewCampaignModal}
            onEditCampaign={openEditCampaignModal}
            onDeleteCampaign={handleDeleteCampaign}
            loading={loading}
            error={error}
          />

          {/* Routes */}
          <Routes>
            <Route path="/" element={<Navigate to="/campaign" replace />} />
            <Route
              path="/campaign"
              element={
                <CampaignPage
                  selectedCampaign={selectedCampaign}
                  campaigns={campaigns}
                  setCampaigns={setCampaigns}
                  setSelectedCampaign={setSelectedCampaign}
                />
              }
            />
            <Route
              path="/posts"
              element={<PostsPage selectedCampaign={selectedCampaign} />}
            />
            <Route
              path="/moodboard"
              element={<MoodBoardPage selectedCampaign={selectedCampaign} />}
            />
            <Route
              path="/metrics"
              element={<MetricsPage selectedCampaign={selectedCampaign} />}
            />
            <Route
              path="/deploy"
              element={<DeployPage selectedCampaign={selectedCampaign} />}
            />
          </Routes>

          {/* Modals */}
          {renderCampaignModal()}
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
