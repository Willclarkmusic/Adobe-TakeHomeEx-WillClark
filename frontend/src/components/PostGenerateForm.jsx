import React, { useState, useEffect } from "react";

/**
 * PostGenerateForm Component - Form for AI post generation
 * Allows user to select product, enter prompt, and choose aspect ratios
 */
function PostGenerateForm({ campaignId, onGenerate, onCancel }) {
  const [products, setProducts] = useState([]);
  const [loadingProducts, setLoadingProducts] = useState(false);

  const [formData, setFormData] = useState({
    product_id: "",
    prompt: "",
    aspect_ratios: ["1:1"] // Default to 1:1
  });

  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");

  // Fetch products for the campaign
  useEffect(() => {
    if (campaignId) {
      fetchProducts();
    }
  }, [campaignId]);

  const fetchProducts = async () => {
    try {
      setLoadingProducts(true);
      const response = await fetch(`/api/products?campaign_id=${campaignId}`);
      if (!response.ok) {
        throw new Error("Failed to fetch products");
      }
      const data = await response.json();
      setProducts(data);

      // Auto-select first product if available
      if (data.length > 0) {
        setFormData(prev => ({ ...prev, product_id: data[0].id }));
      }
    } catch (err) {
      console.error("Error fetching products:", err);
      setError("Failed to load products");
    } finally {
      setLoadingProducts(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Validation
    if (!formData.product_id) {
      setError("Please select a product");
      return;
    }
    if (!formData.prompt.trim()) {
      setError("Please enter a generation prompt");
      return;
    }
    if (formData.aspect_ratios.length === 0) {
      setError("Please select at least one aspect ratio");
      return;
    }

    try {
      setGenerating(true);

      const response = await fetch("/api/posts/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          campaign_id: campaignId,
          product_id: formData.product_id,
          prompt: formData.prompt,
          aspect_ratios: formData.aspect_ratios
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to generate post");
      }

      const generatedPost = await response.json();
      onGenerate(generatedPost);

      // Reset form
      setFormData({
        product_id: products.length > 0 ? products[0].id : "",
        prompt: "",
        aspect_ratios: ["1:1"]
      });
    } catch (err) {
      console.error("Error generating post:", err);
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  };

  const handleAspectRatioToggle = (ratio) => {
    setFormData(prev => {
      const ratios = prev.aspect_ratios.includes(ratio)
        ? prev.aspect_ratios.filter(r => r !== ratio)
        : [...prev.aspect_ratios, ratio];
      return { ...prev, aspect_ratios: ratios };
    });
  };

  if (loadingProducts) {
    return (
      <div className="brutalist-card">
        <p className="font-mono text-lg uppercase">Loading products...</p>
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="brutalist-card bg-yellow-50 dark:bg-yellow-900/20">
        <h3 className="text-xl font-bold uppercase mb-3">⚠️ No Products Available</h3>
        <p className="font-mono text-sm">
          You need to add at least one product to this campaign before generating posts.
          Go to the Campaign tab to add products.
        </p>
        <button onClick={onCancel} className="brutalist-button mt-4">
          Cancel
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Product Selector */}
      <div>
        <label className="block text-lg font-bold uppercase mb-2">
          Select Product
        </label>
        <select
          value={formData.product_id}
          onChange={(e) => setFormData(prev => ({ ...prev, product_id: e.target.value }))}
          className="brutalist-select w-full"
          disabled={generating}
        >
          {products.map(product => (
            <option key={product.id} value={product.id}>
              {product.name}
            </option>
          ))}
        </select>
      </div>

      {/* Prompt Textarea */}
      <div>
        <label className="block text-lg font-bold uppercase mb-2">
          Generation Prompt
        </label>
        <textarea
          value={formData.prompt}
          onChange={(e) => setFormData(prev => ({ ...prev, prompt: e.target.value }))}
          placeholder="E.g., Create an engaging post highlighting the eco-friendly features and summer vibes..."
          className="brutalist-input w-full min-h-[120px] resize-y"
          disabled={generating}
        />
        <p className="text-sm font-mono text-gray-600 dark:text-gray-400 mt-2">
          Describe the tone, style, or specific features you want to highlight in the post.
        </p>
      </div>

      {/* Aspect Ratio Checkboxes */}
      <div>
        <label className="block text-lg font-bold uppercase mb-3">
          Aspect Ratios
        </label>
        <div className="space-y-2">
          <label className="flex items-center space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.aspect_ratios.includes("1:1")}
              onChange={() => handleAspectRatioToggle("1:1")}
              className="w-5 h-5 border-2 border-black dark:border-white"
              disabled={generating}
            />
            <span className="font-mono">
              <strong>1:1</strong> - Instagram Square (1080x1080)
            </span>
          </label>
          <label className="flex items-center space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.aspect_ratios.includes("16:9")}
              onChange={() => handleAspectRatioToggle("16:9")}
              className="w-5 h-5 border-2 border-black dark:border-white"
              disabled={generating}
            />
            <span className="font-mono">
              <strong>16:9</strong> - Landscape/YouTube (1920x1080)
            </span>
          </label>
          <label className="flex items-center space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={formData.aspect_ratios.includes("9:16")}
              onChange={() => handleAspectRatioToggle("9:16")}
              className="w-5 h-5 border-2 border-black dark:border-white"
              disabled={generating}
            />
            <span className="font-mono">
              <strong>9:16</strong> - Story/Vertical (1080x1920)
            </span>
          </label>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="brutalist-card bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-200">
          <p className="font-mono text-sm">❌ {error}</p>
        </div>
      )}

      {/* Loading State */}
      {generating && (
        <div className="brutalist-card bg-blue-50 dark:bg-blue-900/20">
          <p className="font-mono text-lg uppercase">
            🤖 Generating post... This may take 10-20 seconds.
          </p>
          <p className="font-mono text-sm mt-2 text-gray-600 dark:text-gray-400">
            AI is writing copy and compositing images for {formData.aspect_ratios.length} aspect ratio(s)...
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          type="submit"
          disabled={generating}
          className="brutalist-button bg-green-400 dark:bg-green-600 flex-1"
        >
          {generating ? "Generating..." : "🚀 Generate Post"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={generating}
          className="brutalist-button bg-gray-300 dark:bg-gray-700"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

export default PostGenerateForm;
