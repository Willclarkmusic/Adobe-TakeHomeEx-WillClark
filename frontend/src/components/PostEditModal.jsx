import React, { useState, useEffect } from "react";
import Modal from "./Modal";

/**
 * PostEditModal Component - Text Editor + Image Regeneration
 *
 * Allows editing post text content AND regenerating images with new settings.
 */
function PostEditModal({ isOpen, onClose, post, onSave }) {
  const [headline, setHeadline] = useState(post.headline || "");
  const [bodyText, setBodyText] = useState(post.body_text || "");
  const [caption, setCaption] = useState(post.caption || "");
  const [textColor, setTextColor] = useState(post.text_color || "#FF4081");
  const [saving, setSaving] = useState(false);

  // Image regeneration state
  const [regeneratePrompt, setRegeneratePrompt] = useState(
    post.generation_prompt || ""
  );
  const [selectedRatios, setSelectedRatios] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(post.product_id || "");
  const [products, setProducts] = useState([]);
  const [regenerating, setRegenerating] = useState(false);
  const [isRegenerateOpen, setIsRegenerateOpen] = useState(false);

  // Initialize selected ratios based on existing images
  useEffect(() => {
    const ratios = [];
    if (post.image_1_1) ratios.push("1:1");
    if (post.image_16_9) ratios.push("16:9");
    if (post.image_9_16) ratios.push("9:16");
    setSelectedRatios(ratios);
  }, [post]);

  // Fetch products for the campaign
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await fetch(
          `/api/products?campaign_id=${post.campaign_id}`
        );
        if (response.ok) {
          const data = await response.json();
          setProducts(data);
        }
      } catch (err) {
        console.error("Error fetching products:", err);
      }
    };

    if (isOpen) {
      fetchProducts();
    }
  }, [isOpen, post.campaign_id]);

  const handleRatioToggle = (ratio) => {
    setSelectedRatios((prev) =>
      prev.includes(ratio) ? prev.filter((r) => r !== ratio) : [...prev, ratio]
    );
  };

  const handleRegenerate = async () => {
    if (!selectedProduct) {
      alert("Please select a product");
      return;
    }

    if (selectedRatios.length === 0) {
      alert("Please select at least one aspect ratio");
      return;
    }

    const confirmed = window.confirm(
      "⚠️ This will regenerate and REPLACE the existing images. This action cannot be undone. Continue?"
    );

    if (!confirmed) return;

    setRegenerating(true);

    try {
      const response = await fetch(`/api/posts/${post.id}/regenerate`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: regeneratePrompt,
          aspect_ratios: selectedRatios,
          product_id: selectedProduct,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to regenerate images");
      }

      const updatedPost = await response.json();

      if (onSave) {
        onSave(updatedPost);
      }

      alert("✅ Images regenerated successfully!");
      onClose();
    } catch (err) {
      console.error("Error regenerating images:", err);
      alert(`❌ Failed to regenerate images: ${err.message}`);
    } finally {
      setRegenerating(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);

    try {
      const response = await fetch(`/api/posts/${post.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          headline,
          body_text: bodyText,
          caption,
          text_color: textColor,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to update post");
      }

      const updatedPost = await response.json();

      if (onSave) {
        onSave(updatedPost);
      }

      alert("✅ Post updated successfully!");
      onClose();
    } catch (err) {
      console.error("Error updating post:", err);
      alert(`❌ Failed to update post: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Edit Post - ${post.headline}`}
    >
      <div className="space-y-6">
        {/* ========== IMAGE REGENERATION SECTION (ACCORDION) ========== */}
        <div className="border-4 border-black dark:border-white bg-yellow-50 dark:bg-blue-800">
          {/* Accordion Header */}
          <button
            onClick={() => setIsRegenerateOpen(!isRegenerateOpen)}
            className="w-full px-4 py-3 flex items-center justify-between font-bold uppercase text-left hover:bg-yellow-100 dark:hover:bg-blue-950 transition-colors"
          >
            <span className="text-lg">🔄 Regenerate Images</span>
            <span
              className="text-2xl transform transition-transform"
              style={{
                transform: isRegenerateOpen ? "rotate(180deg)" : "rotate(0deg)",
              }}
            >
              ▼
            </span>
          </button>

          {/* Accordion Content */}
          {isRegenerateOpen && (
            <div className="px-4 pb-4 border-t-2 border-black dark:border-white dark:bg-slate-700 pt-4">
              {/* Prompt Input */}
              <div className="mb-3">
                <label className="font-bold text-sm block mb-1">
                  Generation Prompt:
                </label>
                <textarea
                  value={regeneratePrompt}
                  onChange={(e) => setRegeneratePrompt(e.target.value)}
                  className="w-full px-3 py-2 border-2 border-black dark:border-white dark:bg-black font-mono"
                  rows={2}
                  placeholder="Describe how you want the images to look..."
                />
              </div>

              {/* Product Selector */}
              <div className="mb-3">
                <label className="font-bold text-sm block mb-1">Product:</label>
                <select
                  value={selectedProduct}
                  onChange={(e) => setSelectedProduct(e.target.value)}
                  className="w-full px-3 py-2 border-2 border-black dark:border-white dark:bg-black font-mono"
                >
                  <option value="">Select a product...</option>
                  {products.map((product) => (
                    <option key={product.id} value={product.id}>
                      {product.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Aspect Ratio Checkboxes */}
              <div className="mb-3">
                <label className="font-bold text-sm block mb-2">
                  Aspect Ratios:
                </label>
                <div className="flex gap-4">
                  {["1:1", "16:9", "9:16"].map((ratio) => (
                    <label
                      key={ratio}
                      className="flex items-center gap-2 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={selectedRatios.includes(ratio)}
                        onChange={() => handleRatioToggle(ratio)}
                        className="w-4 h-4 cursor-pointer"
                      />
                      <span className="font-mono text-sm">{ratio}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Regenerate Button */}
              <button
                onClick={handleRegenerate}
                disabled={regenerating}
                className="brutalist-button bg-orange-400 dark:bg-orange-600 w-full"
              >
                {regenerating ? "Regenerating..." : "🔄 Regenerate Images"}
              </button>

              <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
                ⚠️ Warning: This will replace existing images and cannot be
                undone.
              </p>
            </div>
          )}
        </div>

        {/* ========== TEXT EDITING SECTION ========== */}
        <div className="border-t-2 border-black dark:border-white pt-4">
          <h3 className="text-lg font-bold uppercase mb-3">
            ✏️ Edit Text Content
          </h3>

          {/* Headline */}
          <div>
            <label className="font-bold text-sm block mb-1">Headline:</label>
            <input
              type="text"
              value={headline}
              onChange={(e) => setHeadline(e.target.value)}
              className="w-full px-3 py-2 border-2 border-black dark:border-white dark:bg-black font-mono"
              maxLength={60}
            />
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
              {headline.length}/60 characters
            </p>
          </div>

          {/* Body Text */}
          <div>
            <label className="font-bold text-sm block mb-1">Body Text:</label>
            <textarea
              value={bodyText}
              onChange={(e) => setBodyText(e.target.value)}
              className="w-full px-3 py-2 border-2 border-black dark:border-white dark:bg-black  font-mono"
              rows={3}
              maxLength={280}
            />
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
              {bodyText.length}/280 characters
            </p>
          </div>

          {/* Caption */}
          <div>
            <label className="font-bold text-sm block mb-1 ">Caption:</label>
            <textarea
              value={caption}
              onChange={(e) => setCaption(e.target.value)}
              className="w-full px-3 py-2 border-2 border-black dark:border-white dark:bg-black font-mono"
              rows={2}
              maxLength={150}
            />
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
              {caption.length}/150 characters
            </p>
          </div>

          {/* Text Color */}
          <div>
            <label className="font-bold text-sm block mb-1">
              Text Color Reference:
            </label>
            <div className="flex items-center gap-2">
              <input
                type="color"
                value={textColor}
                onChange={(e) => setTextColor(e.target.value)}
                className="w-12 h-12 border-2 border-black dark:border-white cursor-pointer"
              />
              <span className="font-mono text-sm">{textColor}</span>
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
              (For reference only - image text is generated by AI)
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 pt-4 border-t-2 border-black dark:border-white">
            <button
              onClick={handleSave}
              disabled={saving}
              className="brutalist-button bg-green-400 dark:bg-green-600 flex-1"
            >
              {saving ? "Saving..." : "Save Text Changes"}
            </button>

            <button
              onClick={onClose}
              className="brutalist-button bg-gray-400 dark:bg-gray-600"
            >
              Cancel
            </button>
          </div>
        </div>
        {/* End Text Editing Section */}
      </div>
    </Modal>
  );
}

export default PostEditModal;
