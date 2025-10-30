import React, { useState, useEffect, forwardRef, useImperativeHandle } from 'react';

/**
 * Campaign form component with manual input and JSON upload support
 * Each distinct function is properly encapsulated in its own method
 */
const CampaignForm = forwardRef(({ campaign, onSave, onCancel, onTabSwitch }, ref) => {
  const [formData, setFormData] = useState({
    name: '',
    campaign_message: '',
    call_to_action: '',
    target_region: '',
    target_audience: '',
    brand_images: [],
    start_date: '',
    duration: '',
    products: []  // For displaying products from JSON
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [jsonFile, setJsonFile] = useState(null);

  useEffect(() => {
    populateFormFromCampaign();
  }, [campaign]);

  // ============ Ref Methods Exposure ============

  useImperativeHandle(ref, () => ({
    handleJsonFileSelect
  }));

  // ============ Form Population Methods ============

  const populateFormFromCampaign = () => {
    if (campaign) {
      setFormData({
        name: campaign.name || '',
        campaign_message: campaign.campaign_message || '',
        call_to_action: campaign.call_to_action || '',
        target_region: campaign.target_region || '',
        target_audience: campaign.target_audience || '',
        brand_images: parseBrandImages(campaign.brand_images),
        start_date: campaign.start_date || '',
        duration: campaign.duration || '',
        products: []  // Products are not shown when editing
      });
    }
  };

  const parseBrandImages = (brandImagesStr) => {
    try {
      return JSON.parse(brandImagesStr || '[]');
    } catch {
      return [];
    }
  };

  const populateFormFromJson = (data) => {
    setFormData({
      name: data.name || formData.name,
      campaign_message: data.campaign_message || formData.campaign_message,
      call_to_action: data.call_to_action || formData.call_to_action,
      target_region: data.target_region || formData.target_region,
      target_audience: data.target_audience || formData.target_audience,
      brand_images: parseBrandImages(data.brand_images),
      start_date: data.start_date || formData.start_date,
      duration: data.duration || formData.duration,
      products: data.products || []  // Store products from JSON
    });
  };

  // ============ Validation Methods ============

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name?.trim()) {
      newErrors.name = 'Campaign name is required';
    }

    if (!formData.campaign_message?.trim()) {
      newErrors.campaign_message = 'Campaign message is required';
    }

    if (!formData.target_region?.trim()) {
      newErrors.target_region = 'Target region is required';
    }

    if (!formData.target_audience?.trim()) {
      newErrors.target_audience = 'Target audience is required';
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

  const handleBrandImageChange = (index, value) => {
    const updatedImages = [...formData.brand_images];
    updatedImages[index] = value;
    updateFormField('brand_images', updatedImages);
  };

  const addBrandImageField = () => {
    updateFormField('brand_images', [...formData.brand_images, '']);
  };

  const removeBrandImageField = (index) => {
    const updatedImages = formData.brand_images.filter((_, i) => i !== index);
    updateFormField('brand_images', updatedImages);
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
      reader.onerror = (e) => reject(new Error('Failed to read file'));
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
      const response = await sendValidationRequest(jsonData);
      handleValidationResponse(response);
    } catch (error) {
      throw new Error(`Validation failed: ${error.message}`);
    }
  };

  const sendValidationRequest = async (data) => {
    const response = await fetch('/api/campaigns/validate', {
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
      const savedCampaign = await submitCampaign();
      handleSubmitSuccess(savedCampaign);
    } catch (error) {
      handleSubmitError(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const submitCampaign = async () => {
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
      throw new Error(error.detail || 'Failed to save campaign');
    }

    return response.json();
  };

  const preparePayload = () => {
    const payload = {
      name: formData.name,
      campaign_message: formData.campaign_message,
      call_to_action: formData.call_to_action || null,
      target_region: formData.target_region,
      target_audience: formData.target_audience,
      brand_images: JSON.stringify(formData.brand_images.filter(img => img.trim())),
      start_date: formData.start_date || null,
      duration: formData.duration ? parseInt(formData.duration) : null
    };

    // Add products if present (only for new campaigns with products from JSON)
    if (formData.products && formData.products.length > 0) {
      payload.products = formData.products;
    }

    return payload;
  };

  const getSubmitEndpoint = () => {
    if (campaign) {
      return `/api/campaigns/${campaign.id}`;
    }
    // Use /with-products endpoint if products are present
    return formData.products && formData.products.length > 0
      ? '/api/campaigns/with-products'
      : '/api/campaigns';
  };

  const getSubmitMethod = () => {
    return campaign ? 'PUT' : 'POST';
  };

  const handleSubmitSuccess = (response) => {
    // If response has a 'campaign' field, extract it (from /with-products endpoint)
    // Otherwise, it's already a campaign object
    const savedCampaign = response.campaign || response;
    resetForm();
    onSave(savedCampaign);
  };

  const handleSubmitError = (error) => {
    setErrors({ submit: error.message });
  };

  const resetForm = () => {
    setFormData({
      name: '',
      campaign_message: '',
      target_region: '',
      target_audience: '',
      brand_images: []
    });
    setErrors({});
    setJsonFile(null);
  };

  // ============ Render Methods ============

  const renderJsonUploadSection = () => {
    return (
      <div className="space-y-4">
        <div className="border-4 border-dashed border-black dark:border-white p-8 text-center">
          <input
            type="file"
            accept=".json"
            onChange={handleJsonFileSelect}
            className="hidden"
            id="json-upload"
            disabled={isSubmitting}
          />
          <label
            htmlFor="json-upload"
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

        <div className="text-sm font-mono text-gray-600 dark:text-gray-400">
          <p className="font-bold mb-2">Expected JSON format:</p>
          <pre className="bg-gray-100 dark:bg-gray-900 p-3 border-2 border-black dark:border-white overflow-x-auto">
{`{
  "name": "Campaign Name",
  "campaign_message": "Your message",
  "target_region": "Region",
  "target_audience": "Audience",
  "brand_images": "[\\"url1\\", \\"url2\\"]"
}`}
          </pre>
        </div>
      </div>
    );
  };

  const renderManualFormFields = () => {
    return (
      <div className="space-y-5">
        {renderTextField(
          'name',
          'Campaign Name *',
          'e.g., Summer 2025 Product Launch'
        )}

        {renderTextField(
          'campaign_message',
          'Campaign Message *',
          'Enter campaign message',
          true
        )}

        {renderTextField(
          'call_to_action',
          'Call to Action',
          'e.g., Shop Now!, Learn More',
          false
        )}

        {renderTextField(
          'target_region',
          'Target Region *',
          'e.g., North America, Europe'
        )}

        {renderTextField(
          'target_audience',
          'Target Audience *',
          'Describe your target audience'
        )}

        {renderScheduleFields()}

        {renderBrandImagesSection()}

        {renderProductsPreview()}
      </div>
    );
  };

  const renderTextField = (name, label, placeholder, multiline = false) => {
    const Component = multiline ? 'textarea' : 'input';
    const extraProps = multiline ? { rows: 3 } : { type: 'text' };

    return (
      <div>
        <label className="block text-sm font-bold uppercase mb-2">
          {label}
        </label>
        <Component
          name={name}
          value={formData[name]}
          onChange={handleFieldChange}
          className="brutalist-input w-full"
          placeholder={placeholder}
          disabled={isSubmitting}
          {...extraProps}
        />
        {errors[name] && renderError(errors[name])}
      </div>
    );
  };

  const renderBrandImagesSection = () => {
    return (
      <div>
        <label className="block text-sm font-bold uppercase mb-2">
          Brand Images (URLs or Paths)
        </label>

        <div className="space-y-4">
          {formData.brand_images.map((image, index) => (
            <div key={index} className="space-y-2">
              {/* Image Preview */}
              {image && renderBrandImagePreview(image, index)}

              {/* Image URL Input */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={image}
                  onChange={(e) => handleBrandImageChange(index, e.target.value)}
                  className="brutalist-input flex-1"
                  placeholder="https://example.com/image.jpg or /static/media/image.jpg"
                  disabled={isSubmitting}
                />
                <button
                  type="button"
                  onClick={() => removeBrandImageField(index)}
                  className="px-4 py-2 border-3 border-black dark:border-white bg-red-500 text-white font-bold uppercase text-sm"
                  disabled={isSubmitting}
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>

        <button
          type="button"
          onClick={addBrandImageField}
          className="mt-3 brutalist-button bg-green-400 dark:bg-green-600"
          disabled={isSubmitting}
        >
          + Add Image
        </button>

        <p className="text-xs font-mono text-gray-500 dark:text-gray-400 mt-2">
          URLs will be automatically downloaded and stored locally
        </p>
      </div>
    );
  };

  const renderBrandImagePreview = (imagePath, index) => {
    return (
      <div className="border-4 border-black dark:border-white overflow-hidden bg-gray-100 dark:bg-gray-800">
        <img
          src={imagePath}
          alt={`Brand Image ${index + 1}`}
          className="w-full h-48 object-cover"
          onError={(e) => {
            e.target.style.display = 'none';
            e.target.nextSibling.style.display = 'flex';
          }}
        />
        <div
          style={{ display: 'none' }}
          className="w-full h-48 flex items-center justify-center text-red-500 font-mono text-xs p-2 text-center"
        >
          ❌ Failed to load preview
        </div>
      </div>
    );
  };

  const renderScheduleFields = () => {
    return (
      <div className="border-4 border-black dark:border-white p-4 bg-yellow-50 dark:bg-yellow-900/20">
        <h3 className="text-sm font-bold uppercase mb-3">📅 Schedule (Optional)</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold uppercase mb-2">
              Start Date
            </label>
            <input
              type="date"
              name="start_date"
              value={formData.start_date}
              onChange={handleFieldChange}
              className="brutalist-input w-full"
              disabled={isSubmitting}
            />
          </div>
          <div>
            <label className="block text-xs font-bold uppercase mb-2">
              Duration (days)
            </label>
            <input
              type="number"
              name="duration"
              value={formData.duration}
              onChange={handleFieldChange}
              placeholder="e.g., 30"
              className="brutalist-input w-full"
              disabled={isSubmitting}
              min="1"
            />
          </div>
        </div>
      </div>
    );
  };

  const renderProductsPreview = () => {
    if (!formData.products || formData.products.length === 0) {
      return null;  // Don't show section if no products
    }

    return (
      <div className="border-4 border-black dark:border-white p-4 bg-blue-50 dark:bg-blue-900/20">
        <h3 className="text-sm font-bold uppercase mb-3">
          📦 Products from JSON ({formData.products.length})
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {formData.products.map((product, index) => renderProductCard(product, index))}
        </div>
        <p className="text-xs font-mono text-gray-600 dark:text-gray-400 mt-3">
          These products will be created with the campaign. Edit them later in the Products section.
        </p>
      </div>
    );
  };

  const renderProductCard = (product, index) => {
    return (
      <div key={index} className="border-3 border-black dark:border-white bg-white dark:bg-gray-800 p-3">
        {product.image_path && (
          <img
            src={product.image_path}
            alt={product.name}
            className="w-full h-32 object-cover border-3 border-black dark:border-white mb-2"
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
        )}
        <h4 className="font-bold text-sm uppercase mb-1">{product.name}</h4>
        <p className="text-xs font-mono text-gray-600 dark:text-gray-400 line-clamp-2">
          {product.description}
        </p>
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
          disabled={isSubmitting}
          className="brutalist-button flex-1 bg-green-400 dark:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Saving...' : (campaign ? 'Update Campaign' : 'Create Campaign')}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="brutalist-button flex-1 bg-gray-300 dark:bg-gray-700 disabled:opacity-50"
        >
          Cancel
        </button>
      </div>
    );
  };

  // ============ Main Render ============

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {renderManualFormFields()}
      {renderSubmitError()}
      {renderActionButtons()}
    </form>
  );
});

// Export JSON upload tab component
export function CampaignFormJsonTab({ campaign, onSave, onCancel }) {
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
          id="campaign-json-upload-tab"
        />
        <label
          htmlFor="campaign-json-upload-tab"
          className="cursor-pointer inline-block brutalist-button bg-blue-400 dark:bg-blue-600"
        >
          📁 Choose JSON File
        </label>
      </div>

      <div className="text-sm font-mono text-gray-600 dark:text-gray-400">
        <p className="font-bold mb-2">Expected JSON format:</p>
        <pre className="bg-gray-100 dark:bg-gray-900 p-3 border-2 border-black dark:border-white overflow-x-auto">
{`{
  "name": "Campaign Name",
  "campaign_message": "Your message",
  "target_region": "Region",
  "target_audience": "Audience",
  "brand_images": "[\\"url1\\", \\"url2\\"]"
}`}
        </pre>
        <p className="mt-3 text-xs">
          💡 If JSON is incomplete, switch to the Manual tab to fill remaining fields.
        </p>
      </div>

      <CampaignForm
        ref={formRef}
        campaign={campaign}
        onSave={onSave}
        onCancel={onCancel}
      />
    </div>
  );
}

export default CampaignForm;
