import React, { useState } from "react";

/**
 * PostCard Component - Compact Instagram-style post card
 * Similar to ProductCard layout with image preview and text below
 */
function PostCard({ post, onEdit, onDelete }) {
  // Track which aspect ratio is being previewed
  const [selectedRatio, setSelectedRatio] = useState(getFirstAvailableRatio());

  function getFirstAvailableRatio() {
    if (post.image_1_1) return "1:1";
    if (post.image_16_9) return "16:9";
    if (post.image_9_16) return "9:16";
    return null;
  }

  const renderPostImage = () => {
    const imagePath =
      selectedRatio === "1:1"
        ? post.image_1_1
        : selectedRatio === "16:9"
        ? post.image_16_9
        : post.image_9_16;

    if (!imagePath) {
      return renderPlaceholderImage();
    }

    return (
      <img
        src={`/static/${imagePath}`}
        alt={post.headline}
        className="w-full h-full object-cover"
        onError={(e) => {
          console.error("Failed to load image:", imagePath);
          e.target.style.display = "none";
          e.target.nextSibling.style.display = "flex";
        }}
      />
    );
  };

  const renderPlaceholderImage = () => {
    return (
      <div className="w-full h-64 bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
        <span className="text-6xl">🎨</span>
      </div>
    );
  };

  const renderAspectRatioSelector = () => {
    const ratios = [];
    if (post.image_1_1) ratios.push({ key: "1:1", label: "Square" });
    if (post.image_16_9) ratios.push({ key: "16:9", label: "Landscape" });
    if (post.image_9_16) ratios.push({ key: "9:16", label: "Story" });

    if (ratios.length <= 1) return null;

    return (
      <div className="flex gap-1 mb-2">
        {ratios.map((ratio) => (
          <button
            key={ratio.key}
            onClick={() => setSelectedRatio(ratio.key)}
            className={`px-2 py-1 text-xs font-bold uppercase border-2 border-black dark:border-white ${
              selectedRatio === ratio.key
                ? "bg-black dark:bg-white text-white dark:text-black"
                : "bg-white dark:bg-black text-black dark:text-white"
            }`}
          >
            {ratio.label}
          </button>
        ))}
      </div>
    );
  };

  const renderTextContent = () => {
    return (
      <div className="flex-1 px-3">
        <h4 className="text-lg font-bold uppercase mb-1 ">{post.headline}</h4>
        <p className="font-bold text-md">Post Body: </p>
        <p className="font-mono text-xs text-gray-700 dark:text-gray-300 mb-2 ">
          {post.body_text}
        </p>
        <p className="font-bold text-md">Caption: </p>
        <p className="font-mono text-xs italic text-gray-600 dark:text-gray-400 ">
          {post.caption}
        </p>
      </div>
    );
  };

  const renderActionButtons = () => {
    return (
      <div className="flex gap-2 mx-auto w-full px-3 pb-3">
        <button
          onClick={() => onEdit && onEdit(post)}
          className="px-3 py-2 border-2 border-black dark:border-white bg-yellow-300 dark:bg-yellow-600 text-black font-bold uppercase text-xs hover:translate-x-0.5 hover:translate-y-0.5 transition-transform flex-1"
        >
          Edit
        </button>
        <a
          href={`/static/${
            post.image_1_1 || post.image_16_9 || post.image_9_16
          }`}
          download
          className="px-3 py-2 border-2 border-black dark:border-white bg-blue-400 dark:bg-blue-600 text-black font-bold uppercase text-xs hover:translate-x-0.5 hover:translate-y-0.5 transition-transform text-center flex-1"
        >
          Download
        </a>
        <button
          onClick={() => onDelete(post.id)}
          className="px-3 py-2 border-2 border-black dark:border-white bg-red-500 text-white font-bold uppercase text-xs hover:translate-x-0.5 hover:translate-y-0.5 transition-transform flex-1"
        >
          Delete
        </button>
      </div>
    );
  };

  return (
    <div className="border-2 border-black dark:border-white overflow-hidden bg-white dark:bg-black">
      {/* Post Image Preview */}
      <div className="relative">
        {renderPostImage()}
        {/* Hidden fallback for image error */}
        <div className="hidden w-full h-64 bg-gray-200 dark:bg-gray-700 items-center justify-center">
          <span className="text-6xl">🎨</span>
        </div>
      </div>

      {/* Aspect Ratio Selector */}
      <div className="px-3 pt-3">{renderAspectRatioSelector()}</div>

      {/* Text Content */}
      <div className="py-2">{renderTextContent()}</div>

      {/* Action Buttons */}
      {renderActionButtons()}
    </div>
  );
}

export default PostCard;
