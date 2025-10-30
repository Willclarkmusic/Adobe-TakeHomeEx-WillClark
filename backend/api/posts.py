"""
Posts API router for CRUD operations and AI post generation.
"""
import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.orm import Post, Campaign, Product
from models.pydantic import PostCreate, PostUpdate, PostRead, PostGenerateRequest
from services.gemini_service import GeminiService
from services.image_compositor import ImageCompositor


router = APIRouter()


@router.get("/posts", response_model=List[PostRead])
async def get_posts(campaign_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get all posts, optionally filtered by campaign_id.
    """
    query = db.query(Post)
    if campaign_id:
        query = query.filter(Post.campaign_id == campaign_id)

    posts = query.order_by(Post.created_at.desc()).all()
    return posts


@router.get("/posts/{post_id}", response_model=PostRead)
async def get_post(post_id: str, db: Session = Depends(get_db)):
    """
    Get a single post by ID.
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/posts", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(post_data: PostCreate, db: Session = Depends(get_db)):
    """
    Create a new post manually (without AI generation).
    """
    # Verify campaign and product exist
    campaign = db.query(Campaign).filter(Campaign.id == post_data.campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    product = db.query(Product).filter(Product.id == post_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Create post
    db_post = Post(
        id=str(uuid.uuid4()),
        campaign_id=post_data.campaign_id,
        product_id=post_data.product_id,
        headline=post_data.headline,
        body_text=post_data.body_text,
        caption=post_data.caption,
        image_1_1=post_data.image_1_1,
        image_16_9=post_data.image_16_9,
        image_9_16=post_data.image_9_16,
        generation_prompt=post_data.generation_prompt
    )

    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post


@router.post("/posts/generate", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def generate_post(request: PostGenerateRequest, db: Session = Depends(get_db)):
    """
    Generate a post using AI (Gemini for text, PIL for images).

    This is the main endpoint that orchestrates:
    1. Fetch campaign and product data
    2. Generate text content using Gemini
    3. Generate images for selected aspect ratios using PIL
    4. Save post to database
    """
    # 1. Fetch campaign data
    campaign = db.query(Campaign).filter(Campaign.id == request.campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # 2. Fetch product data
    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        # 3. Generate text content using Gemini
        gemini_service = GeminiService()
        text_content = await gemini_service.generate_post_copy(
            campaign_message=campaign.campaign_message,
            call_to_action=campaign.call_to_action,
            target_region=campaign.target_region,
            target_audience=campaign.target_audience,
            product_name=product.name,
            product_description=product.description,
            user_prompt=request.prompt
        )

        headline = text_content["headline"]
        body_text = text_content["body_text"]
        caption = text_content["caption"]

        # 4. Generate images for selected aspect ratios
        image_compositor = ImageCompositor()
        brand_images = json.loads(campaign.brand_images) if campaign.brand_images else []

        image_paths = {}
        aspect_ratio_map = {
            "1:1": "1-1",
            "16:9": "16-9",
            "9:16": "9-16"
        }

        for aspect_ratio in request.aspect_ratios:
            if aspect_ratio not in aspect_ratio_map:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid aspect ratio: {aspect_ratio}. Must be one of: 1:1, 16:9, 9:16"
                )

            filename_ratio = aspect_ratio_map[aspect_ratio]
            output_filename = f"image_{filename_ratio}.png"

            image_path = await image_compositor.create_post_image(
                aspect_ratio=aspect_ratio,
                product_image_path=product.image_path,
                brand_images=brand_images,
                headline=headline,
                caption=caption,
                campaign_name=campaign.name,
                output_filename=output_filename
            )

            image_paths[aspect_ratio] = image_path

        # 5. Create Post record in DB
        post_id = str(uuid.uuid4())
        db_post = Post(
            id=post_id,
            campaign_id=request.campaign_id,
            product_id=request.product_id,
            headline=headline,
            body_text=body_text,
            caption=caption,
            image_1_1=image_paths.get("1:1"),
            image_16_9=image_paths.get("16:9"),
            image_9_16=image_paths.get("9:16"),
            generation_prompt=request.prompt
        )

        db.add(db_post)
        db.commit()
        db.refresh(db_post)

        return db_post

    except ValueError as e:
        # Handle Gemini API errors
        raise HTTPException(status_code=400, detail=f"AI generation failed: {str(e)}")
    except Exception as e:
        # Handle other errors
        raise HTTPException(status_code=500, detail=f"Post generation failed: {str(e)}")


@router.put("/posts/{post_id}", response_model=PostRead)
async def update_post(post_id: str, post_data: PostUpdate, db: Session = Depends(get_db)):
    """
    Update an existing post.
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Update fields if provided
    if post_data.headline is not None:
        db_post.headline = post_data.headline
    if post_data.body_text is not None:
        db_post.body_text = post_data.body_text
    if post_data.caption is not None:
        db_post.caption = post_data.caption
    if post_data.image_1_1 is not None:
        db_post.image_1_1 = post_data.image_1_1
    if post_data.image_16_9 is not None:
        db_post.image_16_9 = post_data.image_16_9
    if post_data.image_9_16 is not None:
        db_post.image_9_16 = post_data.image_9_16
    if post_data.generation_prompt is not None:
        db_post.generation_prompt = post_data.generation_prompt

    db.commit()
    db.refresh(db_post)

    return db_post


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: str, db: Session = Depends(get_db)):
    """
    Delete a post and its associated images.
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # TODO: Delete image files from filesystem
    # For now, just delete the database record

    db.delete(db_post)
    db.commit()

    return None
