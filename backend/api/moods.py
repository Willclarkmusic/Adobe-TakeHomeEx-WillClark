"""
Mood Board API endpoints for managing mood media (images and videos).

Handles AI generation, manual uploads, listing, and deletion of mood media.
"""
import logging
import uuid
import json
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from database import get_db
from models.orm import MoodMedia, Campaign, Product
from models.pydantic import (
    MoodMediaRead,
    MoodImageGenerateRequest,
    MoodVideoGenerateRequest,
    MoodAvailableImagesResponse,
    ProductRead
)
from services import mood_service, file_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/moods", tags=["moods"])


@router.get("", response_model=List[MoodMediaRead])
async def list_mood_media(campaign_id: str, db: Session = Depends(get_db)):
    """
    Get all mood media for a campaign, ordered by created_at descending (newest first).

    Args:
        campaign_id: Campaign ID to filter by
        db: Database session

    Returns:
        List of MoodMediaRead objects
    """
    logger.info(f"📋 Fetching mood media for campaign {campaign_id}")

    media = db.query(MoodMedia)\
        .filter(MoodMedia.campaign_id == campaign_id)\
        .order_by(MoodMedia.created_at.desc())\
        .all()

    logger.info(f"  ✓ Found {len(media)} mood media items")
    return media


@router.post("/images/generate", response_model=List[MoodMediaRead])
async def generate_mood_images(
    request: MoodImageGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate 1-3 mood board images (one per ratio).

    Each ratio generates a completely separate image with distinct styling.

    Args:
        request: Generation request with campaign_id, prompt, source_images, ratios
        db: Database session

    Returns:
        List of created MoodMediaRead objects (one per ratio)

    Raises:
        HTTPException: If validation fails or generation errors occur
    """
    logger.info(f"🎨 Generating mood images for campaign {request.campaign_id}")
    logger.info(f"  Ratios: {request.ratios}")
    logger.info(f"  Source images: {len(request.source_images)}")

    # Validate ratios
    if len(request.ratios) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 3 aspect ratios allowed"
        )

    valid_ratios = ["1:1", "3:4", "4:3", "9:16", "16:9"]
    invalid_ratios = [r for r in request.ratios if r not in valid_ratios]
    if invalid_ratios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid aspect ratios: {invalid_ratios}. Valid: {valid_ratios}"
        )

    # Check image size limit (17MB)
    if request.source_images:
        total_size_mb = mood_service.calculate_images_total_size(request.source_images)
        logger.info(f"  Total source images size: {total_size_mb:.2f} MB")

        if total_size_mb > 17:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Source images exceed 17MB limit ({total_size_mb:.1f}MB). "
                       f"Please reduce the number of images."
            )

    try:
        # Generate images (one per ratio)
        mood_media_list = await mood_service.generate_mood_images(
            campaign_id=request.campaign_id,
            prompt=request.prompt,
            source_images=request.source_images,
            ratios=request.ratios,
            db=db
        )

        logger.info(f"✅ Successfully generated {len(mood_media_list)} mood images")
        return mood_media_list

    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mood image generation failed: {str(e)}"
        )


@router.post("/videos/generate", response_model=MoodMediaRead)
async def generate_mood_video(
    request: MoodVideoGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate mood board video with Veo.

    This is an async operation that may take 30-60 seconds to complete.

    Args:
        request: Video generation request
        db: Database session

    Returns:
        Created MoodMediaRead object

    Raises:
        HTTPException: If validation fails or generation errors occur
    """
    logger.info(f"🎬 Generating mood video for campaign {request.campaign_id}")
    logger.info(f"  Ratio: {request.ratio}, Duration: {request.duration}s")
    logger.info(f"  Source images: {len(request.source_images)}")

    # Validate source images (max 3 for Veo)
    if len(request.source_images) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 3 source images for video generation"
        )

    # Validate ratio
    if request.ratio not in ["16:9", "9:16"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video aspect ratio must be 16:9 or 9:16"
        )

    # Validate duration
    if request.duration not in [4, 6, 8]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video duration must be 4, 6, or 8 seconds"
        )

    # Check image size limit
    if request.source_images:
        total_size_mb = mood_service.calculate_images_total_size(request.source_images)
        logger.info(f"  Total source images size: {total_size_mb:.2f} MB")

        if total_size_mb > 17:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Source images exceed 17MB limit ({total_size_mb:.1f}MB)"
            )

    try:
        # Generate video (this will poll until complete - may take 30-60s)
        mood_media = await mood_service.generate_mood_video(
            campaign_id=request.campaign_id,
            prompt=request.prompt,
            source_images=request.source_images,
            ratio=request.ratio,
            duration=request.duration,
            db=db
        )

        logger.info(f"✅ Successfully generated mood video")
        return mood_media

    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except TimeoutError as e:
        logger.error(f"❌ Video generation timed out: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Video generation timed out. Please try again."
        )
    except Exception as e:
        logger.error(f"❌ Video generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mood video generation failed: {str(e)}"
        )


@router.post("/upload", response_model=MoodMediaRead)
async def upload_mood_media(
    campaign_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload mood media file manually (is_generated=False).

    Accepts images and videos. Uploaded files are saved with date-stamped filenames.

    Args:
        campaign_id: Campaign ID
        file: Uploaded file
        db: Database session

    Returns:
        Created MoodMediaRead object

    Raises:
        HTTPException: If file type invalid or upload fails
    """
    logger.info(f"📤 Uploading mood media for campaign {campaign_id}")
    logger.info(f"  File: {file.filename}, Type: {file.content_type}")

    # Validate file type
    if not file.content_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type could not be determined"
        )

    is_image = file.content_type.startswith("image/")
    is_video = file.content_type.startswith("video/")

    if not (is_image or is_video):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only images and videos allowed"
        )

    # Get campaign for name sanitization
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found"
        )

    try:
        # Read file data
        file_data = await file.read()

        # Determine media type
        media_type = "video" if is_video else "image"

        # Generate filename
        campaign_name = mood_service.sanitize_campaign_name(campaign.name, 20)
        date_stamp = mood_service.get_date_stamp()
        ext = file.filename.split(".")[-1] if "." in file.filename else ("mp4" if is_video else "png")
        filename = f"{campaign_name}_upload_{date_stamp}.{ext}"

        # Save file locally
        if is_image:
            file_path = file_manager.save_mood_image(file_data, filename)
        else:
            file_path = file_manager.save_mood_video(file_data, filename)

        logger.info(f"  ✓ Saved locally: {file_path}")

        # Create DB entry (is_generated = False)
        mood_media = MoodMedia(
            id=str(uuid.uuid4()),
            campaign_id=campaign_id,
            file_path=file_path,
            gcs_uri=None,  # Not using GCS
            media_type=media_type,
            is_generated=False,  # Manual upload
            prompt=None,
            source_images=None,
            aspect_ratio=None,  # Could detect from file metadata if needed
            generation_metadata=json.dumps({"original_filename": file.filename}),
            created_at=datetime.utcnow()
        )
        db.add(mood_media)
        db.commit()
        db.refresh(mood_media)

        logger.info(f"✅ Successfully uploaded mood media")
        return mood_media

    except Exception as e:
        logger.error(f"❌ Upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.delete("/{mood_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mood_media(mood_id: str, db: Session = Depends(get_db)):
    """
    Delete mood media from both database and filesystem.

    Args:
        mood_id: Mood media ID
        db: Database session

    Raises:
        HTTPException: If mood media not found
    """
    logger.info(f"🗑️ Deleting mood media {mood_id}")

    # Get mood media
    mood = db.query(MoodMedia).filter(MoodMedia.id == mood_id).first()
    if not mood:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mood media not found"
        )

    try:
        # Delete file from local filesystem
        file_manager.delete_mood_file(mood.file_path)

        # Delete DB entry
        db.delete(mood)
        db.commit()

        logger.info(f"✅ Successfully deleted mood media")
        return None

    except Exception as e:
        logger.error(f"❌ Delete failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete failed: {str(e)}"
        )


@router.get("/available-images", response_model=MoodAvailableImagesResponse)
async def get_available_images(campaign_id: str, db: Session = Depends(get_db)):
    """
    Get available images for mood generation (products + existing mood images).

    Used by MoodPopup component to show selectable images.

    Args:
        campaign_id: Campaign ID
        db: Database session

    Returns:
        MoodAvailableImagesResponse with products and mood_images lists
    """
    logger.info(f"📷 Fetching available images for campaign {campaign_id}")

    # Get products for this campaign
    products = db.query(Product)\
        .filter(Product.campaign_id == campaign_id)\
        .all()

    # Get existing mood images (exclude videos)
    mood_images = db.query(MoodMedia)\
        .filter(MoodMedia.campaign_id == campaign_id)\
        .filter(MoodMedia.media_type == "image")\
        .all()

    logger.info(f"  ✓ Found {len(products)} products, {len(mood_images)} mood images")

    return {
        "products": [ProductRead.from_orm(p) for p in products],
        "mood_images": [MoodMediaRead.from_orm(m) for m in mood_images]
    }
