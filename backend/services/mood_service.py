"""
Mood Board Service for generating and managing mood media (images and videos).

Handles AI generation with Gemini for images and Veo for videos,
file management, and metadata tracking.
"""
import re
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import List
from sqlalchemy.orm import Session

from models.orm import MoodMedia, Campaign
from services.gemini_service import GeminiService
from services import file_manager

logger = logging.getLogger(__name__)


async def generate_mood_images(
    campaign_id: str,
    prompt: str,
    source_images: List[str],
    ratios: List[str],
    db: Session
) -> List[MoodMedia]:
    """
    Generate mood board images for multiple aspect ratios.

    Creates one separate image per ratio using Gemini AI.
    Each image is saved with a unique date-stamped filename.

    Args:
        campaign_id: Campaign ID
        prompt: User's creative direction
        source_images: List of source image paths (products/mood images)
        ratios: List of aspect ratios (max 3)
        db: Database session

    Returns:
        List of created MoodMedia objects
    """
    logger.info(f"🎨 Generating {len(ratios)} mood images for campaign {campaign_id}")

    # Get campaign
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise ValueError(f"Campaign {campaign_id} not found")

    # Sanitize campaign name for filename
    campaign_name = sanitize_campaign_name(campaign.name, max_len=20)

    # Create Gemini service instance
    gemini_service = GeminiService()

    results = []

    for ratio in ratios:
        logger.info(f"  🖼️ Generating image for ratio {ratio}...")

        # Generate image with Gemini
        image_data = await gemini_service.generate_mood_image(
            prompt=prompt,
            source_images=source_images,
            aspect_ratio=ratio
        )

        # Create unique filename with date stamp
        date_stamp = get_date_stamp()
        filename = f"{campaign_name}_img_{date_stamp}_{ratio.replace(':', '-')}.png"

        # Save image locally
        file_path = file_manager.save_mood_image(image_data, filename)
        logger.info(f"  ✅ Saved locally: {file_path}")

        # Create DB entry
        mood_media = MoodMedia(
            id=str(uuid.uuid4()),
            campaign_id=campaign_id,
            file_path=file_path,
            gcs_uri=None,  # Not using GCS
            media_type="image",
            is_generated=True,
            prompt=prompt,
            source_images=json.dumps(source_images),
            aspect_ratio=ratio,
            generation_metadata=json.dumps({"model": "gemini-2.5-flash-image"}),
            created_at=datetime.utcnow()
        )
        db.add(mood_media)
        results.append(mood_media)

    db.commit()

    # Refresh all to get IDs
    for mood in results:
        db.refresh(mood)

    logger.info(f"✅ Successfully generated {len(results)} mood images")
    return results


async def generate_mood_video(
    campaign_id: str,
    prompt: str,
    source_images: List[str],
    ratio: str,
    duration: int,
    db: Session
) -> MoodMedia:
    """
    Generate mood board video with Veo.

    Creates a single video using Gemini Veo with async polling.

    Args:
        campaign_id: Campaign ID
        prompt: User's creative direction
        source_images: List of source image paths (max 3)
        ratio: Aspect ratio ("16:9" or "9:16")
        duration: Video duration in seconds (4, 6, or 8)
        db: Database session

    Returns:
        Created MoodMedia object
    """
    logger.info(f"🎬 Generating mood video for campaign {campaign_id} ({ratio}, {duration}s)")

    # Get campaign
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise ValueError(f"Campaign {campaign_id} not found")

    # Sanitize campaign name for filename
    campaign_name = sanitize_campaign_name(campaign.name, max_len=20)

    # Create Gemini service instance
    gemini_service = GeminiService()

    # Verify reference images exist
    if source_images:
        logger.info(f"  📸 Verifying {len(source_images[:3])} reference images...")
        for img_path in source_images[:3]:  # Max 3 for Veo
            # Check if file exists
            from pathlib import Path
            file_path_obj = Path(f"../files/{img_path}")
            if not file_path_obj.exists():
                file_path_obj = Path(f"files/{img_path}")

            if not file_path_obj.exists():
                raise ValueError(f"Reference image file not found: {img_path}")

            logger.info(f"  ✓ Reference image found: {img_path}")

    # Generate video with Veo (this will poll until complete)
    logger.info("  ⏳ Starting Veo generation (this may take 30-60 seconds)...")
    video_data = await gemini_service.generate_veo_video(
        prompt=prompt,
        source_images=source_images[:3],  # Max 3 for Veo
        aspect_ratio=ratio,
        duration=duration
    )
    logger.info("  ✅ Veo generation complete")

    # Create unique filename with date stamp
    date_stamp = get_date_stamp()
    filename = f"{campaign_name}_vid_{date_stamp}_{ratio.replace(':', '-')}.mp4"

    # Save video locally
    file_path = file_manager.save_mood_video(video_data, filename)
    logger.info(f"  ✅ Saved locally: {file_path}")

    # Create DB entry
    mood_media = MoodMedia(
        id=str(uuid.uuid4()),
        campaign_id=campaign_id,
        file_path=file_path,
        gcs_uri=None,  # Not using GCS
        media_type="video",
        is_generated=True,
        prompt=prompt,
        source_images=json.dumps(source_images),
        aspect_ratio=ratio,
        generation_metadata=json.dumps({
            "model": "veo-3.1-generate-preview",
            "duration": duration
        }),
        created_at=datetime.utcnow()
    )
    db.add(mood_media)
    db.commit()
    db.refresh(mood_media)

    logger.info(f"✅ Successfully generated mood video")
    return mood_media


def calculate_images_total_size(image_paths: List[str]) -> float:
    """
    Calculate total file size of images in MB.

    Args:
        image_paths: List of relative image paths (e.g., "media/image.jpg" or "/static/media/image.jpg")

    Returns:
        Total size in megabytes
    """
    total_bytes = 0

    for path in image_paths:
        # Remove leading slash if present
        clean_path = path.lstrip('/')

        # Remove /static/ prefix if present
        if clean_path.startswith('static/'):
            clean_path = clean_path[7:]  # Remove "static/"

        # Try different possible locations (backend runs from backend/ dir, files are in ../files/)
        possible_paths = [
            Path(f"../files/{clean_path}"),
            Path(f"files/{clean_path}"),
            Path(clean_path)
        ]

        for file_path in possible_paths:
            if file_path.exists():
                total_bytes += file_path.stat().st_size
                break
        else:
            logger.warning(f"  ⚠️ Could not find image: {path}")

    return total_bytes / (1024 * 1024)  # Convert to MB


def sanitize_campaign_name(name: str, max_len: int = 20) -> str:
    """
    Sanitize campaign name for use in filenames.

    Removes special characters, replaces spaces with underscores,
    and truncates to max length.

    Args:
        name: Original campaign name
        max_len: Maximum length (default 20)

    Returns:
        Sanitized filename-safe string
    """
    # Remove special characters
    safe = re.sub(r'[^\w\s-]', '', name)
    # Replace spaces with underscores
    safe = re.sub(r'\s+', '_', safe)
    # Remove consecutive underscores
    safe = re.sub(r'_+', '_', safe)
    # Truncate to max length
    return safe.strip('_')[:max_len]


def get_date_stamp() -> str:
    """
    Generate a unique date-based timestamp for filenames.

    Format: YYYYMMDDHHmmss (e.g., "20250111_143022")

    Returns:
        Date stamp string
    """
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")
