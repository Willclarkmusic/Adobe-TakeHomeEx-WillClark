import React, { useState, useEffect } from "react";
import ProductList from "../components/ProductList";
import ProductForm, { ProductFormJsonTab } from "../components/ProductForm";
import Modal from "../components/Modal";

/**
 * Campaign Page - Shows campaign details, schedule, brand images, and products
 * Extracted from main App component for better organization
 */
function CampaignPage({
  selectedCampaign,
  campaigns,
  setCampaigns,
  setSelectedCampaign,
}) {
  // ============ State Management ============
  const [products, setProducts] = useState([]);
  const [loadingProducts, setLoadingProducts] = useState(false);

  const [showProductModal, setShowProductModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);

  const [scheduleData, setScheduleData] = useState({
    start_date: "",
    duration: "",
  });
  const [isSavingSchedule, setIsSavingSchedule] = useState(false);
  const [scheduleMessage, setScheduleMessage] = useState("");

  // ============ Lifecycle Methods ============

  useEffect(() => {
    if (selectedCampaign) {
      fetchProducts(selectedCampaign.id);
    } else {
      setProducts([]);
    }
  }, [selectedCampaign]);

  useEffect(() => {
    if (selectedCampaign) {
      setScheduleData({
        start_date: selectedCampaign.start_date || "",
        duration: selectedCampaign.duration || "",
      });
      setScheduleMessage("");
    }
  }, [selectedCampaign]);

  // ============ Data Fetching Methods ============

  const fetchProducts = async (campaignId) => {
    try {
      setLoadingProducts(true);
      const data = await sendGetProductsRequest(campaignId);
      setProducts(data);
    } catch (err) {
      console.error("Error fetching products:", err);
      setProducts([]);
    } finally {
      setLoadingProducts(false);
    }
  };

  const sendGetProductsRequest = async (campaignId) => {
    const response = await fetch(`/api/products?campaign_id=${campaignId}`);
    if (!response.ok) {
      throw new Error("Failed to fetch products");
    }
    return response.json();
  };

  // ============ Product Management Methods ============

  const openNewProductModal = () => {
    setEditingProduct(null);
    setShowProductModal(true);
  };

  const openEditProductModal = (product) => {
    setEditingProduct(product);
    setShowProductModal(true);
  };

  const closeProductModal = () => {
    setShowProductModal(false);
    setEditingProduct(null);
  };

  const handleProductSaved = (savedProduct) => {
    // If no product passed (e.g., batch creation), just refresh the entire list
    if (!savedProduct) {
      if (selectedCampaign) {
        fetchProducts(selectedCampaign.id);
      }
    } else if (editingProduct) {
      updateProductInList(savedProduct);
    } else {
      addProductToList(savedProduct);
    }
    closeProductModal();
  };

  const addProductToList = (newProduct) => {
    setProducts((prev) => [...prev, newProduct]);
  };

  const updateProductInList = (updatedProduct) => {
    setProducts((prev) =>
      prev.map((p) => (p.id === updatedProduct.id ? updatedProduct : p))
    );
  };

  const handleDeleteProduct = async (productId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this product?"
    );
    if (!confirmed) return;

    try {
      await sendDeleteProductRequest(productId);
      removeProductFromList(productId);
    } catch (err) {
      console.error("Error deleting product:", err);
      alert("Failed to delete product");
    }
  };

  const sendDeleteProductRequest = async (productId) => {
    const response = await fetch(`/api/products/${productId}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      throw new Error("Failed to delete product");
    }
  };

  const removeProductFromList = (productId) => {
    setProducts((prev) => prev.filter((p) => p.id !== productId));
  };

  // ============ Schedule Management Methods ============

  const handleScheduleFieldChange = (field, value) => {
    setScheduleData((prev) => ({ ...prev, [field]: value }));
    setScheduleMessage(""); // Clear message on change
  };

  const saveSchedule = async () => {
    setIsSavingSchedule(true);
    setScheduleMessage("");

    try {
      const response = await fetch(`/api/campaigns/${selectedCampaign.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start_date: scheduleData.start_date || null,
          duration: scheduleData.duration
            ? parseInt(scheduleData.duration)
            : null,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to save schedule");
      }

      const updatedCampaign = await response.json();
      setSelectedCampaign(updatedCampaign);

      // Update in campaigns list
      setCampaigns((prev) =>
        prev.map((c) => (c.id === updatedCampaign.id ? updatedCampaign : c))
      );

      setScheduleMessage("✓ Schedule saved successfully");
    } catch (error) {
      setScheduleMessage("✗ Failed to save schedule");
    } finally {
      setIsSavingSchedule(false);
    }
  };

  // ============ Helper Methods ============

  const parseBrandImages = (brandImagesStr) => {
    try {
      return JSON.parse(brandImagesStr || "[]");
    } catch {
      return [];
    }
  };

  // ============ Render Methods - Campaign Details ============

  const renderCampaignDetails = () => {
    if (!selectedCampaign) return null;
    return (
      <div className="brutalist-card space-y-6">
        <h2 className="text-3xl font-bold uppercase border-b-4 border-black dark:border-white pb-4">
          Campaign Details
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            {renderCampaignField("Message", selectedCampaign.campaign_message)}
            {selectedCampaign.call_to_action &&
              renderCampaignField(
                "Call to Action",
                selectedCampaign.call_to_action
              )}
          </div>
          <div>
            {renderCampaignField(
              "Target Region",
              selectedCampaign.target_region
            )}
            {renderCampaignField(
              "Target Audience",
              selectedCampaign.target_audience,
              true
            )}
          </div>
        </div>

        {renderBrandImages()}
        {renderScheduleSection()}
      </div>
    );
  };

  const renderCampaignField = (label, value, fullWidth = false) => {
    return (
      <div className={fullWidth ? "md:col-span-2" : ""}>
        <h3 className="text-xl font-bold uppercase">{label}:</h3>
        <p className="font-mono text-lg mb-4">{value}</p>
      </div>
    );
  };

  const renderScheduleSection = () => {
    return (
      <div className="border-0 border-black dark:border-white p-4 bg-yellow-50 dark:bg-yellow-900/20">
        <h3 className="text-xl font-bold uppercase mb-4">📅 Schedule</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <label className="block text-sm font-bold uppercase mb-2">
              Start Date
            </label>
            <input
              type="date"
              value={scheduleData.start_date}
              onChange={(e) =>
                handleScheduleFieldChange("start_date", e.target.value)
              }
              className="brutalist-input w-full"
              disabled={isSavingSchedule}
            />
          </div>
          <div>
            <label className="block text-sm font-bold uppercase mb-2">
              Duration (days)
            </label>
            <input
              type="number"
              value={scheduleData.duration}
              onChange={(e) =>
                handleScheduleFieldChange("duration", e.target.value)
              }
              placeholder="e.g., 30"
              className="brutalist-input w-full"
              disabled={isSavingSchedule}
              min="1"
            />
          </div>
          <div>
            <button
              onClick={saveSchedule}
              disabled={isSavingSchedule}
              className="brutalist-button bg-green-400 dark:bg-green-600 w-full"
            >
              {isSavingSchedule ? "Saving..." : "💾 Save Schedule"}
            </button>
          </div>
        </div>
        {scheduleMessage && (
          <p
            className={`mt-3 font-mono text-sm ${
              scheduleMessage.includes("✓")
                ? "text-green-600 dark:text-green-400"
                : "text-red-600 dark:text-red-400"
            }`}
          >
            {scheduleMessage}
          </p>
        )}
      </div>
    );
  };

  const renderBrandImages = () => {
    const images = parseBrandImages(selectedCampaign.brand_images);
    console.log("Brand images parsed:", images);
    if (!images || images.length === 0) {
      return (
        <div>
          <h3 className="text-xl font-bold uppercase mb-4">Brand Images:</h3>
          <p className="font-mono text-sm text-gray-500 dark:text-gray-400">
            No brand images added
          </p>
        </div>
      );
    }

    return (
      <div>
        <h3 className="text-xl font-bold uppercase mb-4">Brand Images:</h3>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
          {images.map((imagePath, index) => (
            <div
              key={index}
              className="border-4 border-black dark:border-white overflow-hidden bg-gray-100 dark:bg-gray-800"
            >
              <img
                src={imagePath}
                alt={`Brand ${index + 1}`}
                className="w-full h-32 object-cover"
                onError={(e) => {
                  console.error("Failed to load image:", imagePath);
                  e.target.style.display = "none";
                  e.target.nextSibling.style.display = "flex";
                }}
              />
              <div
                style={{ display: "none" }}
                className="w-full h-32 flex items-center justify-center text-red-500 font-mono text-xs p-2 text-center"
              >
                ❌ Failed to load
                <br />
                {imagePath}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // ============ Render Methods - Products Section ============

  const renderProductsSection = () => {
    if (!selectedCampaign) return null;
    return (
      <div className="brutalist-card space-y-6">
        <div className="flex justify-between items-center border-b-4 border-black dark:border-white pb-4">
          <h2 className="text-3xl font-bold uppercase">
            Products ({products.length})
          </h2>
          <button
            onClick={openNewProductModal}
            className="brutalist-button bg-blue-400 dark:bg-blue-600"
          >
            + Add Product
          </button>
        </div>
        {loadingProducts ? (
          <p className="font-mono text-lg uppercase">Loading products...</p>
        ) : (
          <ProductList
            products={products}
            onEdit={openEditProductModal}
            onDelete={handleDeleteProduct}
            onProductUpdate={updateProductInList}
          />
        )}
      </div>
    );
  };

  // ============ Render Methods - Modals ============

  const renderProductModal = () => {
    const renderJsonTab = () => {
      return (
        <ProductFormJsonTab
          campaignId={selectedCampaign?.id}
          product={editingProduct}
          onSave={handleProductSaved}
          onCancel={closeProductModal}
        />
      );
    };

    const renderManualTab = () => {
      return (
        <ProductForm
          campaignId={selectedCampaign?.id}
          product={editingProduct}
          onSave={handleProductSaved}
          onCancel={closeProductModal}
          onTabSwitch={(index) => {
            // Tab switch handled by modal
          }}
        />
      );
    };

    return (
      <Modal
        isOpen={showProductModal}
        onClose={closeProductModal}
        title={editingProduct ? "Edit Product" : "New Product"}
        tabs={[
          { label: "Manual", content: renderManualTab() },
          { label: "JSON", content: renderJsonTab() },
        ]}
      />
    );
  };

  // ============ Main Render ============

  if (!selectedCampaign) {
    return (
      <div className="brutalist-card">
        <p className="font-mono text-lg uppercase">
          ← Select a campaign to view details
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {renderCampaignDetails()}
      {renderProductsSection()}
      {renderProductModal()}
    </div>
  );
}

export default CampaignPage;
