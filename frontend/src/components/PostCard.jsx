import React from "react";

/**
 * PostCard Component - Displays a generated post with images and text content
 */
function PostCard({ post, onDelete }) {
  const renderImageGallery = () => {
    const images = [];

    if (post.image_1_1) {
      images.push({ path: post.image_1_1, ratio: "1:1 (Square)", label: "1:1" });
    }
    if (post.image_16_9) {
      images.push({ path: post.image_16_9, ratio: "16:9 (Landscape)", label: "16:9" });
    }
    if (post.image_9_16) {
      images.push({ path: post.image_9_16, ratio: "9:16 (Vertical)", label: "9:16" });
    }

    if (images.length === 0) {
      return (
        <p className="text-gray-500 dark:text-gray-400 font-mono text-sm">
          No images generated
        </p>
      );
    }

    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {images.map((img, index) => (
          <div key={index} className="space-y-2">
            <div className="border-4 border-black dark:border-white overflow-hidden bg-gray-100 dark:bg-gray-800">
              <img
                src={`/static/${img.path}`}
                alt={`${img.ratio} aspect ratio`}
                className="w-full h-auto object-contain"
                onError={(e) => {
                  console.error("Failed to load image:", img.path);
                  e.target.style.display = "none";
                  e.target.nextSibling.style.display = "flex";
                }}
              />
              <div
                style={{ display: "none" }}
                className="w-full h-48 flex items-center justify-center text-red-500 font-mono text-xs p-2 text-center"
              >
                ❌ Failed to load
                <br />
                {img.path}
              </div>
            </div>
            <div className="flex gap-2">
              <span className="font-bold text-sm">{img.ratio}</span>
              <a
                href={`/static/${img.path}`}
                download
                className="text-sm underline text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200"
              >
                Download
              </a>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderTextContent = () => {
    return (
      <div className="space-y-3 border-4 border-black dark:border-white p-4 bg-gray-50 dark:bg-gray-800">
        <div>
          <h4 className="text-sm font-bold uppercase text-gray-600 dark:text-gray-400">
            Headline
          </h4>
          <p className="font-bold text-xl">{post.headline}</p>
        </div>
        <div>
          <h4 className="text-sm font-bold uppercase text-gray-600 dark:text-gray-400">
            Body Text
          </h4>
          <p className="font-mono text-sm">{post.body_text}</p>
        </div>
        <div>
          <h4 className="text-sm font-bold uppercase text-gray-600 dark:text-gray-400">
            Caption
          </h4>
          <p className="font-mono text-sm italic">{post.caption}</p>
        </div>
        {post.generation_prompt && (
          <div className="pt-3 border-t-2 border-gray-300 dark:border-gray-600">
            <h4 className="text-xs font-bold uppercase text-gray-500 dark:text-gray-500">
              Generation Prompt
            </h4>
            <p className="font-mono text-xs text-gray-600 dark:text-gray-400">
              {post.generation_prompt}
            </p>
          </div>
        )}
      </div>
    );
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  return (
    <div className="brutalist-card space-y-4">
      {/* Header */}
      <div className="flex justify-between items-start border-b-4 border-black dark:border-white pb-4">
        <div>
          <h3 className="text-2xl font-bold uppercase">{post.headline}</h3>
          <p className="text-sm font-mono text-gray-600 dark:text-gray-400 mt-1">
            Generated: {formatDate(post.created_at)}
          </p>
        </div>
        <button
          onClick={() => onDelete(post.id)}
          className="brutalist-button bg-red-500 text-white text-sm"
        >
          🗑️ Delete
        </button>
      </div>

      {/* Text Content */}
      {renderTextContent()}

      {/* Image Gallery */}
      <div>
        <h4 className="text-lg font-bold uppercase mb-3">Generated Images</h4>
        {renderImageGallery()}
      </div>
    </div>
  );
}

export default PostCard;
