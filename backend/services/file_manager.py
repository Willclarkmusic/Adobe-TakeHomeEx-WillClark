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

# Ensure directories exist
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
POSTS_DIR.mkdir(parents=True, exist_ok=True)

# Allowed image extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}


def is_url(path: str) -> bool:
    """Check if a string is a URL."""
    return path.startswith("http://") or path.startswith("https://")


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


async def process_image_path(path: str) -> str:
    """
    Process an image path - if it's a URL, download it and return local path.
    If it's already a local path, return as-is.

    Args:
        path: Image path or URL

    Returns:
        Local path to the image
    """
    if is_url(path):
        local_path = await download_image_from_url(path)
        return local_path if local_path else path
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
