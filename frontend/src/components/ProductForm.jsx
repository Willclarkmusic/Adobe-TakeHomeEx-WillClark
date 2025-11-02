import React, { useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import ProductBatchPreview from './ProductBatchPreview';

/**
 * Product form component with manual input, JSON upload, and image preview
 * Each distinct function is properly encapsulated in its own method
 */
const ProductForm = forwardRef(({ campaignId, product, onSave, onCancel, onTabSwitch }, ref) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    image_path: ''
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [jsonFile, setJsonFile] = useState(null);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  // Batch product state
  const [batchProducts, setBatchProducts] = useState([]);
  const [batchValidationResults, setBatchValidationResults] = useState(null);
  const [showBatchPreview, setShowBatchPreview] = useState(false);

  useEffect(() => {
    populateFormFromProduct();
  }, [product]);

  // ============ Ref Methods Exposure ============

  useImperativeHandle(ref, () => ({
    handleJsonFileSelect
  }));

  // ============ Form Population Methods ============

  const populateFormFromProduct = () => {
    if (product) {
      setFormData({
        name: product.name || '',
        description: product.description || '',
        image_path: product.image_path || ''
      });
    }
  };

  const populateFormFromJson = (data) => {
    setFormData({
      name: data.name || formData.name,
      description: data.description || formData.description,
      image_path: data.image_path || formData.image_path
    });
  };

  // ============ Validation Methods ============

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name?.trim()) {
      newErrors.name = 'Product name is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const clearFieldError = (fieldName) => {
    if (errors[fieldName]) {
      setErrors(prev => ({
        ...prev,
        [fieldName]: undefined
      }));
    }
  };

  // ============ Form Field Change Handlers ============

  const handleFieldChange = (e) => {
    const { name, value } = e.target;
    updateFormField(name, value);
    clearFieldError(name);
  };

  const updateFormField = (fieldName, value) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: value
    }));
  };

  // ============ Image Upload Methods ============

  const handleImageFileSelect = async (e) => {
    const file = e.target.files[0];
    if (file) {
      await uploadImageFile(file);
    }
  };

  const uploadImageFile = async (file) => {
    setUploadingImage(true);
    setErrors(prev => ({ ...prev, image: undefined }));

    try {
      const uploadedPath = await sendImageUploadRequest(file);
      updateFormField('image_path', uploadedPath);
      notifyImageUploadSuccess();
    } catch (error) {
      handleImageUploadError(error);
    } finally {
      setUploadingImage(false);
    }
  };

  const sendImageUploadRequest = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('/api/media/upload', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error('Failed to upload image');
    }

    const result = await response.json();
    return result.file_path;
  };

  const notifyImageUploadSuccess = () => {
    // Could add success notification here
  };

  const handleImageUploadError = (error) => {
    setErrors(prev => ({
      ...prev,
      image: `Image upload failed: ${error.message}`
    }));
  };

  // ============ Drag & Drop Handlers ============

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      const file = files[0];

      // Check if it's an image file
      if (file.type.startsWith('image/')) {
        await uploadImageFile(file);
      } else {
        setErrors(prev => ({
          ...prev,
          image: 'Please drop an image file (PNG, JPG, GIF, etc.)'
        }));
      }
    }
  };

  // ============ JSON File Handling Methods ============

  const handleJsonFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setJsonFile(file);
      processJsonFile(file);
    }
  };

  const processJsonFile = async (file) => {
    try {
      const fileContent = await readFileAsText(file);
      const jsonData = parseJsonContent(fileContent);
      await validateAndProcessJson(jsonData);
    } catch (error) {
      handleJsonError(error);
    }
  };

  const readFileAsText = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsText(file);
    });
  };

  const parseJsonContent = (content) => {
    try {
      return JSON.parse(content);
    } catch {
      throw new Error('Invalid JSON format');
    }
  };

  const validateAndProcessJson = async (jsonData) => {
    try {
      // Detect if batch (array) or single product (object)
      if (Array.isArray(jsonData)) {
        await handleBatchValidation(jsonData);
      } else {
        // Single product flow
        const dataWithCampaign = { ...jsonData, campaign_id: campaignId };
        const response = await sendValidationRequest(dataWithCampaign);
        handleValidationResponse(response);
      }
    } catch (error) {
      throw new Error(`Validation failed: ${error.message}`);
    }
  };

  const handleBatchValidation = async (productsArray) => {
    // Add campaign_id to each product
    const productsWithCampaign = productsArray.map(product => ({
      ...product,
      campaign_id: campaignId
    }));

    // Send batch validation request
    const response = await sendBatchValidationRequest(productsWithCampaign);

    // Store batch data
    setBatchProducts(productsWithCampaign);
    setBatchValidationResults(response);

    // Show preview screen
    setShowBatchPreview(true);

    // Clear any previous errors
    setErrors({});
  };

  const sendBatchValidationRequest = async (productsArray) => {
    const response = await fetch('/api/products/batch/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(productsArray)
    });

    if (!response.ok) {
      throw new Error('Batch validation request failed');
    }

    return response.json();
  };

  const sendValidationRequest = async (data) => {
    const response = await fetch('/api/products/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error('Validation request failed');
    }

    return response.json();
  };

  const handleValidationResponse = (validationResult) => {
    populateFormFromJson(validationResult.data);

    if (!validationResult.is_complete && validationResult.missing_fields.length > 0) {
      notifyIncompleteData(validationResult.missing_fields);
      if (onTabSwitch) {
        onTabSwitch(0); // Switch to manual tab
      }
    } else {
      notifyCompleteData();
    }
  };

  const notifyIncompleteData = (missingFields) => {
    const message = `Incomplete data. Please fill: ${missingFields.join(', ')}`;
    setErrors({ json: message });
  };

  const notifyCompleteData = () => {
    setErrors({ json: 'JSON loaded successfully. Review and submit.' });
  };

  const handleJsonError = (error) => {
    setErrors({ json: error.message });
    setJsonFile(null);
  };

  // ============ Form Submission Methods ============

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const savedProduct = await submitProduct();
      handleSubmitSuccess(savedProduct);
    } catch (error) {
      handleSubmitError(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const submitProduct = async () => {
    const payload = preparePayload();
    const endpoint = getSubmitEndpoint();
    const method = getSubmitMethod();

    const response = await fetch(endpoint, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to save product');
    }

    return response.json();
  };

  const preparePayload = () => {
    if (product) {
      // Update - don't include campaign_id
      return {
        name: formData.name,
        description: formData.description,
        image_path: formData.image_path
      };
    } else {
      // Create - include campaign_id
      return {
        campaign_id: campaignId,
        name: formData.name,
        description: formData.description,
        image_path: formData.image_path
      };
    }
  };

  const getSubmitEndpoint = () => {
    return product
      ? `/api/products/${product.id}`
      : '/api/products';
  };

  const getSubmitMethod = () => {
    return product ? 'PUT' : 'POST';
  };

  const handleSubmitSuccess = (savedProduct) => {
    resetForm();
    onSave(savedProduct);
  };

  const handleSubmitError = (error) => {
    setErrors({ submit: error.message });
  };

  // ============ Batch Submission Methods ============

  const handleBatchConfirm = async (selectedProducts) => {
    setIsSubmitting(true);

    try {
      const createdProducts = await submitBatchProducts(selectedProducts);
      handleBatchSubmitSuccess(createdProducts);
    } catch (error) {
      handleBatchSubmitError(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const submitBatchProducts = async (products) => {
    const response = await fetch('/api/products/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ products })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create products');
    }

    return response.json();
  };

  const handleBatchSubmitSuccess = (createdProducts) => {
    setShowBatchPreview(false);
    setBatchProducts([]);
    setBatchValidationResults(null);
    setJsonFile(null);
    setErrors({
      json: `✅ Success! Created ${createdProducts.length} product${createdProducts.length !== 1 ? 's' : ''}.`
    });

    // Notify parent
    if (onSave) {
      onSave();
    }
  };

  const handleBatchSubmitError = (error) => {
    setErrors({ submit: `Batch creation failed: ${error.message}` });
  };

  const handleBatchCancel = () => {
    setShowBatchPreview(false);
    setBatchProducts([]);
    setBatchValidationResults(null);
    setJsonFile(null);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      image_path: ''
    });
    setErrors({});
    setJsonFile(null);
  };

  // ============ Render Methods ============

  const renderManualFormFields = () => {
    return (
      <div className="space-y-5">
        {renderTextField('name', 'Product Name *', 'Enter product name')}
        {renderTextArea('description', 'Description', 'Enter product description (optional)')}
        {renderImageSection()}
      </div>
    );
  };

  const renderTextField = (name, label, placeholder) => {
    return (
      <div>
        <label className="block text-sm font-bold uppercase mb-2">
          {label}
        </label>
        <input
          type="text"
          name={name}
          value={formData[name]}
          onChange={handleFieldChange}
          className="brutalist-input w-full"
          placeholder={placeholder}
          disabled={isSubmitting}
        />
        {errors[name] && renderError(errors[name])}
      </div>
    );
  };

  const renderTextArea = (name, label, placeholder) => {
    return (
      <div>
        <label className="block text-sm font-bold uppercase mb-2">
          {label}
        </label>
        <textarea
          name={name}
          value={formData[name]}
          onChange={handleFieldChange}
          className="brutalist-input w-full min-h-[100px]"
          placeholder={placeholder}
          disabled={isSubmitting}
        />
      </div>
    );
  };

  const renderImageSection = () => {
    return (
      <div>
        <label className="block text-sm font-bold uppercase mb-2">
          Product Image
        </label>

        {/* Image Preview */}
        {formData.image_path && renderImagePreview()}

        {/* Image URL Input */}
        <input
          type="text"
          name="image_path"
          value={formData.image_path}
          onChange={handleFieldChange}
          className="brutalist-input w-full mb-3"
          placeholder="https://example.com/image.jpg or /static/media/image.jpg"
          disabled={isSubmitting || uploadingImage}
        />

        {/* Drag & Drop Zone (Click or Drop) */}
        <div className="mb-3">
          {/* Hidden file input */}
          <input
            type="file"
            accept="image/*"
            onChange={handleImageFileSelect}
            className="hidden"
            id="image-upload"
            disabled={isSubmitting || uploadingImage}
          />

          {/* Clickable Drag & Drop Zone */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => {
              if (!isSubmitting && !uploadingImage) {
                document.getElementById('image-upload').click();
              }
            }}
            className={`
              border-4 border-dashed p-6 text-center transition-colors cursor-pointer
              ${isDragging
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900'
                : 'border-black dark:border-white bg-gray-50 dark:bg-gray-800'
              }
              ${(isSubmitting || uploadingImage) ? 'opacity-50 pointer-events-none' : ''}
            `}
          >
            <div className="text-2xl mb-2">📎</div>
            <div className="text-sm font-mono">
              {uploadingImage ? (
                <span className="font-bold text-gray-600 dark:text-gray-400">Uploading...</span>
              ) : isDragging ? (
                <span className="font-bold text-blue-600 dark:text-blue-400">Drop image here!</span>
              ) : (
                <span>Click or drag & drop image here</span>
              )}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              PNG, JPG, GIF, WEBP
            </div>
          </div>
        </div>

        {errors.image && renderError(errors.image)}

        <p className="text-xs font-mono text-gray-500 dark:text-gray-400 mt-2">
          Upload a file or enter a URL. URLs will be downloaded and stored locally.
        </p>
      </div>
    );
  };

  const renderImagePreview = () => {
    return (
      <div className="mb-3 border-4 border-black dark:border-white overflow-hidden">
        <img
          src={formData.image_path}
          alt="Preview"
          className="w-full h-48 object-cover"
          onError={(e) => {
            e.target.style.display = 'none';
          }}
        />
      </div>
    );
  };

  const renderJsonUploadSection = () => {
    return (
      <div className="space-y-4">
        <div className="border-4 border-dashed border-black dark:border-white p-8 text-center">
          <input
            type="file"
            accept=".json"
            onChange={handleJsonFileSelect}
            className="hidden"
            id="product-json-upload"
            disabled={isSubmitting}
          />
          <label
            htmlFor="product-json-upload"
            className="cursor-pointer inline-block brutalist-button bg-blue-400 dark:bg-blue-600"
          >
            📁 Choose JSON File
          </label>
          {jsonFile && (
            <p className="mt-4 font-mono text-sm">
              Selected: {jsonFile.name}
            </p>
          )}
        </div>

        {errors.json && renderError(errors.json, !errors.json.includes('success'))}

        {renderJsonFormatExample()}
      </div>
    );
  };

  const renderJsonFormatExample = () => {
    return (
      <div className="text-sm font-mono text-gray-600 dark:text-gray-400">
        <p className="font-bold mb-2">Expected JSON format:</p>
        <pre className="bg-gray-100 dark:bg-gray-900 p-3 border-2 border-black dark:border-white overflow-x-auto">
{`{
  "name": "Product Name",
  "description": "Product description",
  "image_path": "https://example.com/image.jpg"
}`}
        </pre>
      </div>
    );
  };

  const renderError = (message, isError = true) => {
    const colorClass = isError
      ? 'border-red-500 bg-red-50 dark:bg-red-900 text-red-700 dark:text-red-200'
      : 'border-green-500 bg-green-50 dark:bg-green-900 text-green-700 dark:text-green-200';

    return (
      <div className={`border-4 ${colorClass} p-3 mt-2`}>
        <p className="font-mono text-sm">{message}</p>
      </div>
    );
  };

  const renderSubmitError = () => {
    if (!errors.submit) return null;
    return renderError(errors.submit);
  };

  const renderActionButtons = () => {
    return (
      <div className="flex gap-3 pt-4">
        <button
          type="submit"
          disabled={isSubmitting || uploadingImage}
          className="brutalist-button flex-1 bg-green-400 dark:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Saving...' : (product ? 'Update Product' : 'Add Product')}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting || uploadingImage}
          className="brutalist-button flex-1 bg-gray-300 dark:bg-gray-700 disabled:opacity-50"
        >
          Cancel
        </button>
      </div>
    );
  };

  // ============ Main Render ============

  // Show batch preview if batch data is ready
  if (showBatchPreview && batchProducts.length > 0 && batchValidationResults) {
    return (
      <ProductBatchPreview
        products={batchProducts}
        validationResults={batchValidationResults}
        onConfirm={handleBatchConfirm}
        onCancel={handleBatchCancel}
      />
    );
  }

  // Otherwise, show normal form
  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {renderManualFormFields()}
      {renderSubmitError()}
      {renderActionButtons()}
    </form>
  );
});

// Export JSON upload tab component
export function ProductFormJsonTab({ campaignId, product, onSave, onCancel }) {
  const formRef = React.useRef(null);

  const handleJsonFileSelect = async (e) => {
    const file = e.target.files[0];
    if (file && formRef.current) {
      formRef.current.handleJsonFileSelect({ target: { files: [file] } });
    }
  };

  return (
    <div className="space-y-4">
      <div className="border-4 border-dashed border-black dark:border-white p-8 text-center">
        <input
          type="file"
          accept=".json"
          onChange={handleJsonFileSelect}
          className="hidden"
          id="product-json-upload-tab"
        />
        <label
          htmlFor="product-json-upload-tab"
          className="cursor-pointer inline-block brutalist-button bg-blue-400 dark:bg-blue-600"
        >
          📁 Choose JSON File
        </label>
      </div>

      <div className="text-sm font-mono text-gray-600 dark:text-gray-400">
        <p className="font-bold mb-2">Expected JSON format:</p>
        <pre className="bg-gray-100 dark:bg-gray-900 p-3 border-2 border-black dark:border-white overflow-x-auto">
{`{
  "name": "Product Name",
  "description": "Product description",
  "image_path": "https://example.com/image.jpg"
}`}
        </pre>
        <p className="mt-3 text-xs">
          💡 If JSON is incomplete, switch to the Manual tab to fill remaining fields.
        </p>
      </div>

      <ProductForm
        ref={formRef}
        campaignId={campaignId}
        product={product}
        onSave={onSave}
        onCancel={onCancel}
      />
    </div>
  );
}

export default ProductForm;
