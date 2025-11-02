import React, { useState } from 'react';

/**
 * ProductBatchPreview Component
 *
 * Displays a grid of products for batch approval/rejection before creation.
 * Shows validation status and allows users to select which products to create.
 */
function ProductBatchPreview({ products, validationResults, onConfirm, onCancel }) {
  const [selectedProducts, setSelectedProducts] = useState(
    products.map((_, index) => {
      // Auto-select valid products, deselect invalid ones
      const isValid = validationResults.valid_products.some(
        vp => vp.name === products[index].name
      );
      return isValid;
    })
  );

  const handleToggle = (index) => {
    setSelectedProducts(prev => {
      const newSelected = [...prev];
      newSelected[index] = !newSelected[index];
      return newSelected;
    });
  };

  const handleSelectAll = () => {
    setSelectedProducts(products.map(() => true));
  };

  const handleDeselectAll = () => {
    setSelectedProducts(products.map(() => false));
  };

  const handleConfirm = () => {
    const selectedProductData = products.filter((_, index) => selectedProducts[index]);
    onConfirm(selectedProductData);
  };

  const getProductValidation = (index) => {
    const product = products[index];

    // Check if product is in invalid list
    const invalidProduct = validationResults.invalid_products.find(
      ip => ip.index === index
    );

    if (invalidProduct) {
      return {
        isValid: false,
        error: invalidProduct.errors
      };
    }

    return {
      isValid: true,
      error: null
    };
  };

  const selectedCount = selectedProducts.filter(Boolean).length;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="border-4 border-black dark:border-white p-4 bg-blue-50 dark:bg-blue-900">
        <h3 className="text-lg font-bold uppercase mb-2">📦 Batch Product Preview</h3>
        <p className="text-sm font-mono">
          Review and select products to create. {selectedCount} of {products.length} selected.
        </p>
      </div>

      {/* Selection Actions */}
      <div className="flex gap-3">
        <button
          onClick={handleSelectAll}
          className="brutalist-button bg-green-400 dark:bg-green-600"
        >
          ✅ Select All
        </button>
        <button
          onClick={handleDeselectAll}
          className="brutalist-button bg-gray-400 dark:bg-gray-600"
        >
          ❌ Deselect All
        </button>
      </div>

      {/* Products Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto p-2">
        {products.map((product, index) => {
          const validation = getProductValidation(index);
          const isSelected = selectedProducts[index];

          return (
            <div
              key={index}
              className={`
                border-4 p-4 transition-all cursor-pointer
                ${isSelected
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-900'
                  : 'border-black dark:border-white bg-white dark:bg-gray-800'
                }
                ${!validation.isValid ? 'opacity-60' : ''}
              `}
              onClick={() => handleToggle(index)}
            >
              {/* Checkbox */}
              <div className="flex items-center gap-2 mb-3">
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => handleToggle(index)}
                  className="w-5 h-5 cursor-pointer"
                />
                <span className="font-mono text-xs text-gray-600 dark:text-gray-400">
                  #{index + 1}
                </span>
                <span className="ml-auto">
                  {validation.isValid ? (
                    <span className="text-green-600 dark:text-green-400 font-bold">✅</span>
                  ) : (
                    <span className="text-red-600 dark:text-red-400 font-bold">⚠️</span>
                  )}
                </span>
              </div>

              {/* Image Preview */}
              {product.image_path && (
                <div className="mb-3 border-2 border-black dark:border-white overflow-hidden h-32">
                  <img
                    src={product.image_path}
                    alt={product.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                </div>
              )}

              {/* Product Info */}
              <div>
                <h4 className="font-bold text-sm mb-1 truncate">{product.name}</h4>
                {product.description && (
                  <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">
                    {product.description}
                  </p>
                )}
              </div>

              {/* Validation Error */}
              {!validation.isValid && (
                <div className="mt-2 p-2 bg-red-100 dark:bg-red-900 border-2 border-red-500 text-xs">
                  <span className="font-mono text-red-700 dark:text-red-300">
                    {validation.error}
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 pt-4 border-t-4 border-black dark:border-white">
        <button
          onClick={handleConfirm}
          disabled={selectedCount === 0}
          className={`
            brutalist-button flex-1
            ${selectedCount > 0
              ? 'bg-green-400 dark:bg-green-600'
              : 'bg-gray-400 dark:bg-gray-600 opacity-50 cursor-not-allowed'
            }
          `}
        >
          ✅ Create {selectedCount} Product{selectedCount !== 1 ? 's' : ''}
        </button>
        <button
          onClick={onCancel}
          className="brutalist-button bg-red-400 dark:bg-red-600"
        >
          ❌ Cancel
        </button>
      </div>
    </div>
  );
}

export default ProductBatchPreview;
