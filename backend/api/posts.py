"""
Posts API router for CRUD operations and AI post generation.
"""
import uuid
import json
import re
import logging
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.orm import Post, Campaign, Product
from models.pydantic import PostCreate, PostUpdate, PostRead, PostGenerateRequest, PostRegenerateRequest
from services.gemini_service import GeminiService
from services.image_compositor import ImageCompositor

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


router = APIRouter()


def _sanitize_filename(name: str) -> str:
    """
    Sanitize string for use in filename.
    Remove special characters, replace spaces with underscores.
    (Same logic as ImageCompositor)
    """
    # Remove special characters
    name = re.sub(r'[^\w\s-]', '', name)
    # Replace spaces with underscores
    name = re.sub(r'\s+', '_', name)
    # Remove consecutive underscores
    name = re.sub(r'_+', '_', name)
    return name.strip('_')


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
    Generate a post using AI (Gemini for text and images).

    This is the main endpoint that orchestrates:
    1. Fetch campaign and product data
    2. Generate text content using Gemini
    3. Generate stylized images with text using Gemini (img2img)
    4. Add logo overlay and border to images
    5. Save post to database
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

        # Track the first generated image for consistency across aspect ratios
        base_generated_image = None
        first_aspect_ratio = True

        for aspect_ratio in request.aspect_ratios:
            if aspect_ratio not in aspect_ratio_map:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid aspect ratio: {aspect_ratio}. Must be one of: 1:1, 16:9, 9:16"
                )

            logger.info(f"   🎨 Processing {aspect_ratio} image...")

            # Step 4a: Generate or adapt the image
            if product_pil_image:
                if first_aspect_ratio:
                    # First ratio: Generate from product image (img2img)
                    logger.info(f"      🤖 Step 4a: Generating base image with Gemini from product...")
                    generated_image = await gemini_service.generate_product_image(
                        product_image=product_pil_image,
                        campaign_message=campaign.campaign_message,
                        headline=headline,
                        user_prompt=request.prompt,
                        aspect_ratio=aspect_ratio
                    )
                    base_generated_image = generated_image
                    first_aspect_ratio = False
                    logger.info(f"      ✅ Base image generated! This will be adapted for other ratios.")
                else:
                    # Subsequent ratios: Adapt the base image to new aspect ratio
                    logger.info(f"      🔄 Step 4a: Adapting base image to {aspect_ratio}...")
                    generated_image = await gemini_service.generate_product_image_adaptation(
                        base_image=base_generated_image,
                        headline=headline,
                        new_aspect_ratio=aspect_ratio
                    )
                    logger.info(f"      ✅ Image adapted from base image!")
            else:
                generated_image = None
                logger.info("      ⚠️  Skipping Gemini generation (no product image)")

            filename_ratio = aspect_ratio_map[aspect_ratio]
            output_filename = f"image_{filename_ratio}.png"

            # Step 4b: Composite logo and border onto Gemini image
            logger.info("      🖼️  Step 4b: Adding logo and border to Gemini image...")

            image_path = await image_compositor.create_post_image(
                aspect_ratio=aspect_ratio,
                generated_image=generated_image,  # Gemini image already has text
                brand_images=brand_images,
                campaign_name=campaign.name,
                post_headline=headline,
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


@router.put("/posts/{post_id}/regenerate", response_model=PostRead)
async def regenerate_post_images(
    post_id: str,
    request: PostRegenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Regenerate images for an existing post with new settings.
    Deletes old images and generates new ones.
    """
    logger.info(f"🔄 Starting image regeneration for post {post_id}")

    # 1. Get the post
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # 2. Get campaign and product
    campaign = db.query(Campaign).filter(Campaign.id == db_post.campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 3. Delete old image folder
    safe_campaign = _sanitize_filename(campaign.name)
    safe_headline = _sanitize_filename(db_post.headline)[:50]
    folder_name = f"{safe_campaign}_{safe_headline}"

    base_dir = Path(__file__).resolve().parent.parent.parent
    files_dir = base_dir / "files"
    posts_dir = files_dir / "posts"
    post_folder = posts_dir / folder_name

    if post_folder.exists() and post_folder.is_dir():
        try:
            shutil.rmtree(post_folder)
            logger.info(f"   🗑️  Deleted old images folder: {post_folder}")
        except Exception as e:
            logger.error(f"   ⚠️  Failed to delete old folder: {str(e)}")

    try:
        # 4. Load product image
        if product.image_path:
            logger.info(f"   📦 Loading product image: {product.image_path}")
            from PIL import Image as PILImage

            product_img_path = files_dir / product.image_path.lstrip('/static/')
            product_pil_image = PILImage.open(product_img_path)
            logger.info(f"   ✅ Product image loaded: {product_pil_image.size}")
        else:
            product_pil_image = None
            logger.info(f"   ⚠️  No product image available")

        # 5. Generate new images using existing headline, body, caption, color
        gemini_service = GeminiService()
        image_compositor = ImageCompositor()
        brand_images = json.loads(campaign.brand_images) if campaign.brand_images else []

        image_paths = {}
        aspect_ratio_map = {
            "1:1": "1-1",
            "16:9": "16-9",
            "9:16": "9-16"
        }

        # Track the first generated image for consistency
        base_generated_image = None
        first_aspect_ratio = True

        for aspect_ratio in request.aspect_ratios:
            if aspect_ratio not in aspect_ratio_map:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid aspect ratio: {aspect_ratio}"
                )

            logger.info(f"   🎨 Processing {aspect_ratio} image...")

            # Generate or adapt image
            if product_pil_image:
                if first_aspect_ratio:
                    logger.info(f"      🤖 Generating base image from product...")
                    generated_image = await gemini_service.generate_product_image(
                        product_image=product_pil_image,
                        campaign_message=campaign.campaign_message,
                        headline=db_post.headline,
                        user_prompt=request.prompt,
                        aspect_ratio=aspect_ratio
                    )
                    base_generated_image = generated_image
                    first_aspect_ratio = False
                    logger.info(f"      ✅ Base image generated!")
                else:
                    logger.info(f"      🔄 Adapting base image to {aspect_ratio}...")
                    generated_image = await gemini_service.generate_product_image_adaptation(
                        base_image=base_generated_image,
                        headline=db_post.headline,
                        new_aspect_ratio=aspect_ratio
                    )
                    logger.info(f"      ✅ Image adapted!")
            else:
                generated_image = None
                logger.info(f"      ⚠️  No product image")

            filename_ratio = aspect_ratio_map[aspect_ratio]
            output_filename = f"image_{filename_ratio}.png"

            # Composite logo and border
            logger.info(f"      🖼️  Adding logo and border...")
            image_path = await image_compositor.create_post_image(
                aspect_ratio=aspect_ratio,
                generated_image=generated_image,
                brand_images=brand_images,
                campaign_name=campaign.name,
                post_headline=db_post.headline,
                output_filename=output_filename
            )

            image_paths[aspect_ratio] = image_path
            logger.info(f"   ✅ {aspect_ratio} image saved to: {image_path}")

        # 6. Update post with new image paths and prompt
        db_post.image_1_1 = image_paths.get("1:1")
        db_post.image_16_9 = image_paths.get("16:9")
        db_post.image_9_16 = image_paths.get("9:16")
        db_post.generation_prompt = request.prompt

        db.commit()
        db.refresh(db_post)

        logger.info(f"🎉 Image regeneration complete for post {post_id}")
        return db_post

    except Exception as e:
        logger.error(f"❌ Image regeneration failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image regeneration failed: {str(e)}")


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: str, db: Session = Depends(get_db)):
    """
    Delete a post and its associated images from both database and filesystem.
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Get campaign to construct folder path
    campaign = db.query(Campaign).filter(Campaign.id == db_post.campaign_id).first()

    if campaign:
        # Construct the folder path using same logic as ImageCompositor
        safe_campaign = _sanitize_filename(campaign.name)
        safe_headline = _sanitize_filename(db_post.headline)[:50]
        folder_name = f"{safe_campaign}_{safe_headline}"

        # Build full path to post folder
        base_dir = Path(__file__).resolve().parent.parent.parent
        files_dir = base_dir / "files"
        posts_dir = files_dir / "posts"
        post_folder = posts_dir / folder_name

        # Delete folder if it exists
        if post_folder.exists() and post_folder.is_dir():
            try:
                shutil.rmtree(post_folder)
                logger.info(f"🗑️  Deleted post folder: {post_folder}")
            except Exception as e:
                logger.error(f"⚠️  Failed to delete post folder {post_folder}: {str(e)}")
                # Continue with database deletion even if file deletion fails
        else:
            logger.info(f"ℹ️  Post folder not found (may have been already deleted): {post_folder}")

    # Delete database record
    db.delete(db_post)
    db.commit()
    logger.info(f"✅ Post {post_id} deleted from database")

    return None
