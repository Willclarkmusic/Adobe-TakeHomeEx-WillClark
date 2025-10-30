"""
Posts API router for CRUD operations and AI post generation.
"""
import uuid
import json
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.orm import Post, Campaign, Product
from models.pydantic import PostCreate, PostUpdate, PostRead, PostGenerateRequest
from services.gemini_service import GeminiService
from services.image_compositor import ImageCompositor

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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
        text_color=post_data.text_color,
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
    logger.info(f"🚀 Starting post generation for campaign: {request.campaign_id}, product: {request.product_id}")

    # 1. Fetch campaign data
    logger.info("📂 Step 1: Fetching campaign data...")
    campaign = db.query(Campaign).filter(Campaign.id == request.campaign_id).first()
    if not campaign:
        logger.error(f"❌ Campaign not found: {request.campaign_id}")
        raise HTTPException(status_code=404, detail="Campaign not found")
    logger.info(f"✅ Campaign found: {campaign.name}")

    # 2. Fetch product data
    logger.info("📦 Step 2: Fetching product data...")
    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        logger.error(f"❌ Product not found: {request.product_id}")
        raise HTTPException(status_code=404, detail="Product not found")
    logger.info(f"✅ Product found: {product.name}")

    try:
        # 3. Generate text content using Gemini
        logger.info("🤖 Step 3: Generating text content with Gemini 2.5 Flash...")
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
        text_color = text_content["text_color"]

        logger.info(f"✅ Text generated successfully!")
        logger.info(f"   📝 Headline: {headline}")
        logger.info(f"   🎨 Text Color: {text_color}")

        # 4. Generate images for selected aspect ratios using Gemini + compositing
        logger.info(f"🖼️  Step 4: Generating images for {len(request.aspect_ratios)} aspect ratio(s)...")

        # Load product image for Gemini img2img generation
        if product.image_path:
            logger.info(f"   📦 Loading product image: {product.image_path}")
            from PIL import Image as PILImage
            from pathlib import Path

            # Load the product image
            files_dir = Path(__file__).resolve().parent.parent.parent / "files"
            product_img_path = files_dir / product.image_path.lstrip('/static/')
            product_pil_image = PILImage.open(product_img_path)
            logger.info(f"   ✅ Product image loaded: {product_pil_image.size}")
        else:
            product_pil_image = None
            logger.info(f"   ⚠️  No product image available")

        image_compositor = ImageCompositor()
        brand_images = json.loads(campaign.brand_images) if campaign.brand_images else []
        logger.info(f"   Brand images loaded: {len(brand_images)} image(s)")

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

            logger.info(f"   🎨 Processing {aspect_ratio} image...")

            # Step 4a: Generate stylized image with Gemini (img2img)
            if product_pil_image:
                logger.info(f"      🤖 Step 4a: Generating stylized image with Gemini...")
                generated_image = await gemini_service.generate_product_image(
                    product_image=product_pil_image,
                    campaign_message=campaign.campaign_message,
                    headline=headline,
                    user_prompt=request.prompt,
                    aspect_ratio=aspect_ratio
                )
                logger.info(f"      ✅ Gemini generated stylized image!")
            else:
                generated_image = None
                logger.info(f"      ⚠️  Skipping Gemini generation (no product image)")

            # Step 4b: Composite headline text onto the Gemini-generated image
            logger.info(f"      ✏️  Step 4b: Adding headline overlay to generated image...")
            filename_ratio = aspect_ratio_map[aspect_ratio]
            output_filename = f"image_{filename_ratio}.png"

            image_path = await image_compositor.create_post_image(
                aspect_ratio=aspect_ratio,
                generated_image=generated_image,  # Use Gemini-generated image
                brand_images=brand_images,
                headline=headline,
                text_color=text_color,
                campaign_name=campaign.name,
                output_filename=output_filename
            )

            image_paths[aspect_ratio] = image_path
            logger.info(f"   ✅ {aspect_ratio} image complete and saved to: {image_path}")

        # 5. Create Post record in DB
        logger.info("💾 Step 5: Saving post to database...")
        post_id = str(uuid.uuid4())
        db_post = Post(
            id=post_id,
            campaign_id=request.campaign_id,
            product_id=request.product_id,
            headline=headline,
            body_text=body_text,
            caption=caption,
            text_color=text_color,
            image_1_1=image_paths.get("1:1"),
            image_16_9=image_paths.get("16:9"),
            image_9_16=image_paths.get("9:16"),
            generation_prompt=request.prompt
        )

        db.add(db_post)
        db.commit()
        db.refresh(db_post)

        logger.info(f"🎉 Post generation complete! Post ID: {post_id}")
        return db_post

    except ValueError as e:
        # Handle Gemini API errors
        logger.error(f"❌ AI generation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"AI generation failed: {str(e)}")
    except Exception as e:
        # Handle other errors
        logger.error(f"❌ Post generation failed: {str(e)}", exc_info=True)
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
    if post_data.text_color is not None:
        db_post.text_color = post_data.text_color
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
