import React, { useState } from "react";

/**
 * Product list component with image display
 * Each rendering concern is separated into its own method
 */
function ProductList({ products, onEdit, onDelete, onProductUpdate }) {
  // ============ State Management ============

  const [failedImages, setFailedImages] = useState(new Set());
  const [regeneratingProducts, setRegeneratingProducts] = useState(new Set());
  const [confirmModal, setConfirmModal] = useState({
    show: false,
    product: null
  });

  // ============ Validation Methods ============

  const hasProducts = () => {
    return products && products.length > 0;
  };

  const hasImage = (product) => {
    return product.image_path && product.image_path.trim();
  };

  const isImageFailed = (product) => {
    return failedImages.has(product.id);
  };

  const isRegenerating = (product) => {
    return regeneratingProducts.has(product.id);
  };

  // ============ Render Helper Methods ============

  const renderEmptyState = () => {
    return (
      <div className="brutalist-card bg-gray-50 dark:bg-gray-900">
        <p className="text-lg font-mono text-gray-500 dark:text-gray-400 uppercase">
          No products yet. Add your first product!
        </p>
      </div>
    );
  };

  const renderProductImage = (product) => {
    // Show generate button if image failed or missing
    if (!hasImage(product) || isImageFailed(product)) {
      return renderGenerateImageButton(product);
    }

    return (
      <img
        src={product.image_path}
        alt={product.name}
        className="w-full h-48 object-cover border-black dark:border-white"
        onError={(e) => handleImageError(e, product)}
      />
    );
  };

  const renderGenerateImageButton = (product) => {
    return (
      <div className="w-full h-48 border-4 border-black dark:border-white bg-gray-200 dark:bg-gray-700 flex flex-col items-center justify-center gap-3">
        {isRegenerating(product) ? (
          <>
            <span className="text-5xl animate-pulse">🎨</span>
            <p className="font-mono text-sm font-bold uppercase">Generating...</p>
          </>
        ) : (
          <>
            <span className="text-5xl">🖼️</span>
            <button
              onClick={() => openConfirmModal(product)}
              className="px-4 py-2 border-3 border-black dark:border-white bg-green-400 dark:bg-green-600 text-black dark:text-white font-bold uppercase text-sm hover:translate-x-1 hover:translate-y-1 transition-transform"
              disabled={isRegenerating(product)}
            >
              🎨 Generate Image
            </button>
          </>
        )}
      </div>
    );
  };

  const handleImageError = (e, product) => {
    console.error(`Failed to load image for product: ${product.name}`);
    // Mark this product's image as failed
    setFailedImages(prev => new Set(prev).add(product.id));
  };

  const renderProductDetails = (product) => {
    return (
      <div className="flex-1">
        <h4 className="text-2xl font-bold uppercase mb-2">{product.name}</h4>

        {renderDescription(product)}
        {/* {renderImageInfo(product)} */}
        {/* {renderProductId(product)} */}
      </div>
    );
  };

  const renderDescription = (product) => {
    if (!product.description) return null;

    return (
      <p className="font-mono text-sm mb-3 text-gray-700 dark:text-gray-300">
        {product.description}
      </p>
    );
  };

  const renderImageInfo = (product) => {
    if (!hasImage(product)) return null;

    return (
      <div className="mt-3">
        <span className="font-mono text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 border-2 border-black dark:border-white">
          🖼️ {extractImageFilename(product.image_path)}
        </span>
      </div>
    );
  };

  const extractImageFilename = (path) => {
    return path.split("/").pop() || path;
  };

  // const renderProductId = (product) => {
  //   return (
  //     <p className="font-mono text-xs text-gray-500 dark:text-gray-400 mt-3">
  //       ID: {product.id}
  //     </p>
  //   );
  // };

  const renderActionButtons = (product) => {
    return (
      <div className="flex flex-row w-40 mx-auto gap-2">
        {renderEditButton(product)}
        {renderDeleteButton(product)}
      </div>
    );
  };

  const renderEditButton = (product) => {
    return (
      <button
        onClick={() => handleEdit(product)}
        className="px-4 py-2 border-3 border-black dark:border-white bg-yellow-300 dark:bg-yellow-600 text-black font-bold uppercase text-sm hover:translate-x-1 hover:translate-y-1 transition-transform"
        aria-label={`Edit ${product.name}`}
      >
        Edit
      </button>
    );
  };

  const renderDeleteButton = (product) => {
    return (
      <button
        onClick={() => handleDelete(product.id, product.name)}
        className="px-4 py-2 border-3 border-black dark:border-white bg-red-500 dark:bg-red-700 text-white font-bold uppercase text-sm hover:translate-x-1 hover:translate-y-1 transition-transform"
        aria-label={`Delete ${product.name}`}
      >
        Delete
      </button>
    );
  };

  const renderProduct = (product) => {
    return (
      <div
        key={product.id}
        className="border-2 overflow-hidden p-0 brutalist-card"
      >
        {/* Product Image */}
        <div className="flex relative">
          {renderProductImage(product)}
          {/* Hidden fallback for image error */}
          <div className="hidden w-full h-48 border-4 border-black dark:border-white bg-gray-200 dark:bg-gray-700 items-center justify-center">
            <span className="text-6xl">📦</span>
          </div>
        </div>

        {/* Product Content */}
        <div className="p-3 flex justify-between items-start gap-4">
          {renderProductDetails(product)}
        </div>
        <div className="m-2 relative align-bottom ">
          {renderActionButtons(product)}
        </div>
      </div>
    );
  };

  // ============ Event Handlers ============

  const handleEdit = (product) => {
    if (onEdit) {
      onEdit(product);
    }
  };

  const handleDelete = (productId, productName) => {
    if (onDelete) {
      onDelete(productId);
    }
  };

  const openConfirmModal = (product) => {
    setConfirmModal({
      show: true,
      product
    });
  };

  const closeConfirmModal = () => {
    setConfirmModal({
      show: false,
      product: null
    });
  };

  const handleRegenerateImage = async () => {
    const product = confirmModal.product;
    if (!product) return;

    // Close modal
    closeConfirmModal();

    // Mark as regenerating
    setRegeneratingProducts(prev => new Set(prev).add(product.id));

    try {
      const response = await fetch(`/api/products/${product.id}/regenerate-image`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({})
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to regenerate image");
      }

      const updatedProduct = await response.json();

      // Remove from failed images set
      setFailedImages(prev => {
        const newSet = new Set(prev);
        newSet.delete(product.id);
        return newSet;
      });

      // Notify parent component to update the product list
      if (onProductUpdate) {
        onProductUpdate(updatedProduct);
      }

      console.log("✅ Product image regenerated successfully");
    } catch (error) {
      console.error("❌ Image regeneration failed:", error);
      alert(`Failed to regenerate image: ${error.message}`);
    } finally {
      // Remove from regenerating set
      setRegeneratingProducts(prev => {
        const newSet = new Set(prev);
        newSet.delete(product.id);
        return newSet;
      });
    }
  };

  // ============ Main Render ============

  if (!hasProducts()) {
    return renderEmptyState();
  }

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {products.filter(product => product != null).map((product) => renderProduct(product))}
      </div>

      {/* Confirmation Modal */}
      {confirmModal.show && confirmModal.product && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="brutalist-card bg-white dark:bg-gray-800 max-w-md w-full">
            <h3 className="text-2xl font-bold uppercase mb-4">
              Regenerate Image?
            </h3>
            <p className="font-mono text-sm mb-4 text-gray-700 dark:text-gray-300">
              Are you sure you want to regenerate the image for <strong>{confirmModal.product.name}</strong>?
            </p>
            <p className="font-mono text-xs mb-6 text-gray-600 dark:text-gray-400">
              This will use AI to generate a new product photo based on the product name and description.
            </p>
            <div className="flex gap-3">
              <button
                onClick={handleRegenerateImage}
                className="brutalist-button bg-green-400 dark:bg-green-600 flex-1"
              >
                Yes, Regenerate
              </button>
              <button
                onClick={closeConfirmModal}
                className="brutalist-button bg-gray-300 dark:bg-gray-700"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default ProductList;
