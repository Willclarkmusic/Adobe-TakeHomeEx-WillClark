"""
File management service for handling image uploads and URL downloads.
"""
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional
import httpx
from fastapi import UploadFile


# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_DIR = BASE_DIR / "files" / "media"
POSTS_DIR = BASE_DIR / "files" / "posts"
MOODS_DIR = BASE_DIR / "files" / "moods"

# Ensure directories exist
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
POSTS_DIR.mkdir(parents=True, exist_ok=True)
MOODS_DIR.mkdir(parents=True, exist_ok=True)

# Allowed image extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}


def is_url(path: str) -> bool:
    """Check if a string is a URL."""
    return path.startswith("http://") or path.startswith("https://")


def is_local_file_path(path: str) -> bool:
    """
    Check if a string is a local file path (relative or absolute).
    Excludes URLs and already-processed /static/ paths.

    Args:
        path: String to check

    Returns:
        True if it looks like a local file path, False otherwise
    """
    if not path:
        return False
    if is_url(path):
        return False
    if path.startswith("/static/"):
        return False
    # Check if it looks like a file path (contains path separator or has extension)
    return "/" in path or "\\" in path or Path(path).suffix != ""


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    return Path(filename).suffix.lower()


async def download_image_from_url(url: str) -> Optional[str]:
    """
    Download an image from a URL and save it locally.

    Args:
        url: The URL of the image to download

    Returns:
        Relative path to the saved file (e.g., "/static/media/image_uuid.jpg")
        or None if download failed
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()

            # Determine file extension from content-type or URL
            content_type = response.headers.get("content-type", "")
            if "image/jpeg" in content_type or "image/jpg" in content_type:
                ext = ".jpg"
            elif "image/png" in content_type:
                ext = ".png"
            elif "image/gif" in content_type:
                ext = ".gif"
            elif "image/webp" in content_type:
                ext = ".webp"
            elif "image/svg" in content_type:
                ext = ".svg"
            else:
                # Try to get extension from URL
                ext = get_file_extension(url.split("?")[0])
                if ext not in ALLOWED_EXTENSIONS:
                    ext = ".jpg"  # Default

            # Generate unique filename
            filename = f"image_{uuid.uuid4()}{ext}"
            filepath = MEDIA_DIR / filename

            # Save the file
            with open(filepath, "wb") as f:
                f.write(response.content)

            return f"/static/media/{filename}"

    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return None


async def save_uploaded_file(file: UploadFile) -> Optional[str]:
    """
    Save an uploaded file to the media directory.

    Args:
        file: The uploaded file

    Returns:
        Relative path to the saved file or None if save failed
    """
    try:
        # Validate file extension
        ext = get_file_extension(file.filename)
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"File type {ext} not allowed. Allowed types: {ALLOWED_EXTENSIONS}")

        # Generate unique filename
        filename = f"upload_{uuid.uuid4()}{ext}"
        filepath = MEDIA_DIR / filename

        # Save the file
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return f"/static/media/{filename}"

    except Exception as e:
        print(f"Error saving uploaded file: {e}")
        return None
    finally:
        file.file.close()


async def copy_local_file_to_media(file_path: str) -> Optional[str]:
    """
    Copy a local file to the media directory.

    Args:
        file_path: Relative or absolute path to local file

    Returns:
        Relative path (e.g., "/static/media/image_uuid.jpg") or None if failed
    """
    try:
        # Resolve path (handle both relative and absolute)
        source_path = Path(file_path)

        # If relative, resolve from BASE_DIR
        if not source_path.is_absolute():
            source_path = BASE_DIR / file_path

        if not source_path.exists():
            print(f"❌ Local file not found: {source_path}")
            return None

        # Validate file extension
        ext = get_file_extension(source_path.name)
        if ext not in ALLOWED_EXTENSIONS:
            print(f"❌ File type {ext} not allowed: {source_path}")
            return None

        # Generate unique filename
        filename = f"image_{uuid.uuid4()}{ext}"
        dest_path = MEDIA_DIR / filename

        # Copy file
        shutil.copy2(source_path, dest_path)
        print(f"✅ Copied local file: {file_path} → {dest_path}")

        return f"/static/media/{filename}"

    except Exception as e:
        print(f"❌ Error copying local file {file_path}: {e}")
        return None


async def process_image_path(path: str) -> str:
    """
    Process an image path:
    - If URL: download and return local path
    - If local file: copy to media and return local path
    - If already /static/: return as-is

    Args:
        path: Image path (URL, local file, or /static/ path)

    Returns:
        Local path to the image (/static/media/...)
    """
    if not path:
        return path

    # Already processed (/static/media/...)
    if path.startswith("/static/"):
        return path

    # URL - download it
    if is_url(path):
        local_path = await download_image_from_url(path)
        return local_path if local_path else path

    # Local file path - copy it
    if is_local_file_path(path):
        local_path = await copy_local_file_to_media(path)
        return local_path if local_path else path

    # Unknown format - return as-is
    return path


def delete_file(path: str) -> bool:
    """
    Delete a file from the filesystem.

    Args:
        path: Relative path starting with /static/media/ or /static/posts/

    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert relative path to absolute
        if path.startswith("/static/media/"):
            filename = path.replace("/static/media/", "")
            filepath = MEDIA_DIR / filename
        elif path.startswith("/static/posts/"):
            filename = path.replace("/static/posts/", "")
            filepath = POSTS_DIR / filename
        else:
            return False

        if filepath.exists():
            filepath.unlink()
            return True
        return False

    except Exception as e:
        print(f"Error deleting file {path}: {e}")
        return False


def save_mood_image(image_data: bytes, filename: str) -> str:
    """
    Save mood board image to /files/moods/ directory.

    Args:
        image_data: Image bytes (PNG format)
        filename: Desired filename (e.g., "Summer2025_img_20250111_143022_1-1.png")

    Returns:
        Relative path (e.g., "moods/Summer2025_img_20250111_143022_1-1.png")
    """
    try:
        filepath = MOODS_DIR / filename

        with open(filepath, "wb") as f:
            f.write(image_data)

        return f"moods/{filename}"

    except Exception as e:
        raise Exception(f"Failed to save mood image: {str(e)}")


def save_mood_video(video_data: bytes, filename: str) -> str:
    """
    Save mood board video to /files/moods/ directory.

    Args:
        video_data: Video bytes (MP4 format)
        filename: Desired filename (e.g., "Summer2025_vid_20250111_143022_16-9.mp4")

    Returns:
        Relative path (e.g., "moods/Summer2025_vid_20250111_143022_16-9.mp4")
    """
    try:
        filepath = MOODS_DIR / filename

        with open(filepath, "wb") as f:
            f.write(video_data)

        return f"moods/{filename}"

    except Exception as e:
        raise Exception(f"Failed to save mood video: {str(e)}")


def delete_mood_file(file_path: str) -> bool:
    """
    Delete mood media file from filesystem.

    Args:
        file_path: Relative path (e.g., "moods/Summer2025_img_20250111_143022_1-1.png")

    Returns:
        True if successful, False otherwise
    """
    try:
        # Handle both formats: "moods/file.png" and "/static/moods/file.png"
        if file_path.startswith("/static/moods/"):
            clean_path = file_path.replace("/static/moods/", "")
        elif file_path.startswith("moods/"):
            clean_path = file_path.replace("moods/", "")
        else:
            clean_path = file_path

        filepath = MOODS_DIR / clean_path

        if filepath.exists():
            filepath.unlink()
            print(f"✓ Deleted mood file: {file_path}")
            return True

        print(f"⚠️ Mood file not found: {file_path}")
        return False

    except Exception as e:
        print(f"Error deleting mood file {file_path}: {e}")
        return False


async def save_generated_product_image(image, product_name: str) -> str:
    """
    Save a generated product image to /files/media/ directory.

    Args:
        image: PIL Image object to save
        product_name: Product name (will be sanitized for filename)

    Returns:
        Relative path (e.g., "/static/media/product_Tent_abc123.png")

    Raises:
        Exception: If image save fails
    """
    try:
        # Import PIL here to avoid circular imports
        from PIL import Image as PILImage
        import re
        import io

        # Sanitize product name for filename
        # Remove special characters, replace spaces with underscores, lowercase
        sanitized_name = re.sub(r'[^\w\s-]', '', product_name)
        sanitized_name = re.sub(r'[-\s]+', '_', sanitized_name)
        sanitized_name = sanitized_name.strip('_')[:30]  # Max 30 chars

        # Generate unique filename
        filename = f"product_{sanitized_name}_{uuid.uuid4().hex[:8]}.png"
        filepath = MEDIA_DIR / filename

        # Save the PIL Image
        image.save(filepath, format='PNG', quality=95)
        print(f"✅ Saved generated product image: {filename}")

        return f"/static/media/{filename}"

    except Exception as e:
        raise Exception(f"Failed to save generated product image: {str(e)}")
