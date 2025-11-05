"""
Deploy API endpoints for social media posting and scheduling via Ayrshare.

Handles:
- Fetching connected social media profiles
- Scheduling posts (immediate, future, recurring)
- Listing scheduled posts
- Canceling scheduled posts
"""
import logging
import uuid
import json
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from models.orm import ScheduledPost, Post, Campaign
from models.pydantic import (
    AyrshareProfilesResponse,
    AyrshareProfile,
    SchedulePostRequest,
    ScheduledPostRead
)
from services.ayrshare_service import AyrshareService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/deploy", tags=["deploy"])


@router.get("/profiles", response_model=AyrshareProfilesResponse)
async def get_connected_profiles():
    """
    Get all connected social media profiles from Ayrshare.
    """
    logger.info("📱 Fetching connected social media profiles...")

    try:
        ayrshare = AyrshareService()
        profiles = await ayrshare.get_profiles()

        logger.info(f"  ✓ Retrieved {len(profiles)} profiles")
        return {"profiles": [AyrshareProfile(**p) for p in profiles]}

    except Exception as e:
        logger.error(f"❌ Failed to fetch profiles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch connected profiles: {str(e)}"
        )


@router.post("/schedule-post", response_model=ScheduledPostRead)
async def schedule_post(
    request: SchedulePostRequest,
    db: Session = Depends(get_db)
):
    """
    Schedule a social media post via Ayrshare.
    Supports three scheduling types:
    - immediate: Post ~10 seconds from now
    - scheduled: Post at specific future time
    - recurring: Auto-repost multiple times with interval
    """
    logger.info(f"📅 Scheduling post {request.post_id} ({request.schedule_type})...")

    # Validate post exists
    post = db.query(Post).filter(Post.id == request.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post {request.post_id} not found"
        )

    # Validate campaign exists
    campaign = db.query(Campaign).filter(Campaign.id == request.campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {request.campaign_id} not found"
        )

    # Validate schedule_type
    if request.schedule_type not in ["immediate", "scheduled", "recurring"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="schedule_type must be 'immediate', 'scheduled', or 'recurring'"
        )

    # Validate schedule_time for scheduled posts
    if request.schedule_type == "scheduled" and not request.schedule_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="schedule_time required for scheduled posts"
        )

    # Validate recurring_config for recurring posts
    if request.schedule_type == "recurring" and not request.recurring_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="recurring_config required for recurring posts"
        )

    try:
        ayrshare = AyrshareService()

        # Build post text (caption + body_text)
        post_text = f"{post.caption}\n\n{post.body_text}".strip()

        # Build media URLs (use first available aspect ratio)
        # Get absolute URL for post images
        media_urls = []
        if post.image_1_1:
            # Assuming your app is served at a public URL
            # For local testing, you may need ngrok or similar
            base_url = "http://localhost:8000"  # TODO: Make this configurable
            media_urls.append(f"{base_url}/static/{post.image_1_1}")
        elif post.image_16_9:
            base_url = "http://localhost:8000"
            media_urls.append(f"{base_url}/static/{post.image_16_9}")
        elif post.image_9_16:
            base_url = "http://localhost:8000"
            media_urls.append(f"{base_url}/static/{post.image_9_16}")

        # Call Ayrshare API based on schedule_type
        ayrshare_response = None

        if request.schedule_type == "immediate":
            logger.info("  ⚡ Posting immediately...")
            ayrshare_response = await ayrshare.post_immediate(
                post_text=post_text,
                platforms=request.platforms,
                media_urls=media_urls
            )

        elif request.schedule_type == "scheduled":
            logger.info(f"  📅 Scheduling for {request.schedule_time}...")
            ayrshare_response = await ayrshare.post_scheduled(
                post_text=post_text,
                platforms=request.platforms,
                schedule_time=request.schedule_time,
                media_urls=media_urls
            )

        elif request.schedule_type == "recurring":
            logger.info("  🔁 Creating recurring post...")
            # For recurring posts, we need to handle multiple posts
            # Ayrshare Auto Repost feature only works with single post
            # So we'll schedule the first one and track the config

            recurring_config = request.recurring_config
            start_time = request.schedule_time or datetime.utcnow()

            ayrshare_response = await ayrshare.post_recurring(
                post_text=post_text,
                platforms=request.platforms,
                repeat=recurring_config.repeat,
                days_interval=recurring_config.days,
                start_time=start_time,
                media_urls=media_urls
            )

        # Create database record
        scheduled_post = ScheduledPost(
            id=str(uuid.uuid4()),
            post_id=request.post_id,
            campaign_id=request.campaign_id,
            schedule_type=request.schedule_type,
            platforms=json.dumps(request.platforms),
            schedule_time=request.schedule_time,
            recurring_config=json.dumps(recurring_config.dict()) if request.recurring_config else None,
            ayrshare_post_id=ayrshare_response.get("id"),
            status="pending" if request.schedule_type != "immediate" else "posted",
            error_message=None,
            created_at=datetime.utcnow()
        )
        db.add(scheduled_post)
        db.commit()
        db.refresh(scheduled_post)

        logger.info(f"✅ Successfully scheduled post: {scheduled_post.id}")

        # Return with nested post data
        scheduled_post.post = post
        return scheduled_post

    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Scheduling failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to schedule post: {str(e)}"
        )


@router.get("/scheduled-posts", response_model=List[ScheduledPostRead])
async def list_scheduled_posts(
    campaign_id: str = Query(..., description="Campaign ID to filter by"),
    db: Session = Depends(get_db)
):
    """
    Get all scheduled posts for a campaign.
    """
    logger.info(f"📋 Fetching scheduled posts for campaign {campaign_id}...")

    # Validate campaign exists
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found"
        )

    # Get scheduled posts with nested post data
    scheduled_posts = db.query(ScheduledPost)\
        .filter(ScheduledPost.campaign_id == campaign_id)\
        .order_by(ScheduledPost.created_at.desc())\
        .all()

    # Attach post data
    for sp in scheduled_posts:
        sp.post = db.query(Post).filter(Post.id == sp.post_id).first()

    logger.info(f"  ✓ Found {len(scheduled_posts)} scheduled posts")
    return scheduled_posts


@router.delete("/scheduled-posts/{scheduled_post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_scheduled_post(
    scheduled_post_id: str,
    db: Session = Depends(get_db)
):
    """
    Cancel/delete a scheduled post.
    Deletes from both Ayrshare and local database.
    """
    logger.info(f"🗑️ Canceling scheduled post {scheduled_post_id}...")

    # Get scheduled post
    scheduled_post = db.query(ScheduledPost)\
        .filter(ScheduledPost.id == scheduled_post_id)\
        .first()

    if not scheduled_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found"
        )

    try:
        # Delete from Ayrshare if we have an ID
        if scheduled_post.ayrshare_post_id:
            ayrshare = AyrshareService()
            await ayrshare.delete_post(scheduled_post.ayrshare_post_id)
            logger.info("  ✓ Deleted from Ayrshare")

        # Delete from database
        db.delete(scheduled_post)
        db.commit()

        logger.info("✅ Successfully canceled scheduled post")
        return None

    except Exception as _:
        logger.error(f"❌ Failed to cancel post: {str(_)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel scheduled post: {str(_)}"
        )
