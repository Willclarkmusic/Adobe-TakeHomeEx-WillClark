import React, { useState } from 'react';

/**
 * Modal component with tab support for Manual and JSON input modes
 */
function Modal({ isOpen, onClose, title, children, tabs = null }) {
  const [activeTab, setActiveTab] = useState(0);

  if (!isOpen) return null;

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleTabChange = (index) => {
    setActiveTab(index);
  };

  const renderTabs = () => {
    if (!tabs || tabs.length === 0) return null;

    return (
      <div className="flex border-b-4 border-black dark:border-white mb-6">
        {tabs.map((tab, index) => (
          <button
            key={index}
            onClick={() => handleTabChange(index)}
            className={`
              px-6 py-3 font-bold uppercase text-sm border-r-4 border-black dark:border-white last:border-r-0
              ${activeTab === index
                ? 'bg-yellow-300 dark:bg-yellow-600 text-black'
                : 'bg-white dark:bg-gray-800 text-black dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
              }
            `}
          >
            {tab.label}
          </button>
        ))}
      </div>
    );
  };

  const renderContent = () => {
    if (tabs && tabs.length > 0) {
      return tabs[activeTab].content;
    }
    return children;
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4"
      onClick={handleBackdropClick}
    >
      <div className="brutalist-card max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-start mb-6 pb-4 border-b-4 border-black dark:border-white">
          <h2 className="text-3xl font-bold uppercase">{title}</h2>
          <button
            onClick={onClose}
            className="text-3xl font-bold hover:text-red-600 dark:hover:text-red-400"
            aria-label="Close modal"
          >
            ×
          </button>
        </div>

        {/* Tabs */}
        {renderTabs()}

        {/* Content */}
        <div className="modal-content">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}

export default Modal;
