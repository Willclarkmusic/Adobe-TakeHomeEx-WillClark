import React from "react";

/**
 * Product list component with image display
 * Each rendering concern is separated into its own method
 */
function ProductList({ products, onEdit, onDelete }) {
  // ============ Validation Methods ============

  const hasProducts = () => {
    return products && products.length > 0;
  };

  const hasImage = (product) => {
    return product.image_path && product.image_path.trim();
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
    if (!hasImage(product)) {
      return renderPlaceholderImage();
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

  const renderPlaceholderImage = () => {
    return (
      <div className="w-full h-48 border-4 border-black dark:border-white bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
        <span className="text-6xl">📦</span>
      </div>
    );
  };

  const handleImageError = (e, product) => {
    console.error(`Failed to load image for product: ${product.name}`);
    e.target.style.display = "none";
    e.target.nextElementSibling.style.display = "flex";
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

  // ============ Main Render ============

  if (!hasProducts()) {
    return renderEmptyState();
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {products.filter(product => product != null).map((product) => renderProduct(product))}
    </div>
  );
}

export default ProductList;
