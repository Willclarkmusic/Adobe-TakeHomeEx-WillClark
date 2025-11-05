"""
Image Compositing Service for generating social media post images.

Uses PIL/Pillow to composite product images, brand elements, and text overlays
into professionally designed post images for multiple aspect ratios.
"""
import re
import logging
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw
import httpx

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ImageCompositor:
    """
    Service for compositing post images with product photos, brand elements, and text.
    """

    # Canvas dimensions for each aspect ratio
    CANVAS_SIZES = {
        "1:1": (1080, 1080),      # Instagram square
        "16:9": (1920, 1080),     # Landscape/YouTube
        "9:16": (1080, 1920)      # Story/Vertical
    }

    def __init__(self):
        """
        Initialize the image compositor.
        """
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.files_dir = self.base_dir / "files"
        self.posts_dir = self.files_dir / "posts"
        self.posts_dir.mkdir(parents=True, exist_ok=True)

    async def create_post_image(
        self,
        aspect_ratio: str,
        generated_image: Optional[Image.Image],
        brand_logo: Optional[str],
        campaign_name: str,
        post_headline: str,
        output_filename: str
    ) -> str:
        """
        Create a post image from Gemini-generated image with logo and border.

        Args:
            aspect_ratio: One of "1:1", "16:9", "9:16"
            generated_image: PIL Image from Gemini (already has text on it)
            brand_logo: Path to brand logo image (randomly selected by caller)
            campaign_name: Campaign name for folder organization
            post_headline: Post headline for folder naming
            output_filename: Filename for the output image (e.g., "image_1-1.png")

        Returns:
            Relative path to the created image (e.g., "posts/CampaignName_Headline/image_1-1.png")
        """
        if aspect_ratio not in self.CANVAS_SIZES:
            raise ValueError(f"Invalid aspect ratio: {aspect_ratio}. Must be one of {list(self.CANVAS_SIZES.keys())}")

        # Get canvas size
        canvas_width, canvas_height = self.CANVAS_SIZES[aspect_ratio]
        logger.info(f"      Target size: {canvas_width}x{canvas_height}")

        # Use Gemini-generated image as the base, or create white canvas
        if generated_image:
            logger.info(f"      Using Gemini-generated image as base ({generated_image.size})")

            # Check if Gemini gave us the exact size we need
            if generated_image.size == (canvas_width, canvas_height):
                canvas = generated_image
            else:
                # Use cover/crop approach to avoid stretching
                logger.info("      Adjusting image to canvas size without stretching...")
                canvas = self._resize_cover_crop(generated_image, canvas_width, canvas_height)
        else:
            canvas = Image.new('RGB', (canvas_width, canvas_height), color='white')

        # Add brand logo overlay
        if brand_logo:
            logger.info(f"      Adding brand logo overlay from: {brand_logo}")
            canvas = await self._add_brand_overlay(canvas, brand_logo, aspect_ratio)
        else:
            logger.info("      No brand logo provided")

        # Add border for neo-brutalist aesthetic
        canvas = self._add_border(canvas)

        # Save image
        output_path = self._save_image(canvas, campaign_name, post_headline, output_filename)
        logger.info(f"      Image saved to: {output_path}")

        return output_path

    async def _add_brand_overlay(self, canvas: Image.Image, brand_path: str, aspect_ratio: str) -> Image.Image:
        """
        Add brand logo as small overlay/watermark.
        """
        try:
            # Load brand image
            brand_img = await self._load_image(brand_path)

            # Resize brand logo to small size
            max_size = 120 if aspect_ratio == "9:16" else 150
            brand_img = self._resize_to_fit(brand_img, max_size, max_size)

            # Add slight transparency
            if brand_img.mode != 'RGBA':
                brand_img = brand_img.convert('RGBA')

            # Position in bottom-right corner
            canvas_width, canvas_height = canvas.size
            x = canvas_width - brand_img.width - 30
            y = canvas_height - brand_img.height - 30

            # Paste brand logo
            canvas.paste(brand_img, (x, y), brand_img)

            return canvas

        except Exception as e:
            print(f"Warning: Failed to add brand overlay: {e}")
            return canvas

    def _add_border(self, canvas: Image.Image, border_width: int = 8) -> Image.Image:
        """
        Add a bold border for neo-brutalist aesthetic.
        """
        draw = ImageDraw.Draw(canvas)
        width, height = canvas.size

        # Draw thick black border
        for i in range(border_width):
            draw.rectangle([i, i, width - 1 - i, height - 1 - i], outline=(0, 0, 0))

        return canvas

    def _resize_to_fit(self, image: Image.Image, max_width: int, max_height: int) -> Image.Image:
        """
        Resize image to fit within max dimensions while maintaining aspect ratio.
        """
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        return image

    def _resize_cover_crop(self, image: Image.Image, target_width: int, target_height: int) -> Image.Image:
        """
        Resize and crop image to cover target dimensions without stretching.
        Uses the 'cover' approach: scales the image to fill the target dimensions,
        maintaining aspect ratio, then crops the overflow.
        """
        source_width, source_height = image.size
        source_ratio = source_width / source_height
        target_ratio = target_width / target_height

        # Calculate scale to cover (not fit)
        if source_ratio > target_ratio:
            # Source is wider - scale based on height
            scale = target_height / source_height
        else:
            # Source is taller or same ratio - scale based on width
            scale = target_width / source_width

        # Resize maintaining aspect ratio
        new_width = int(source_width * scale)
        new_height = int(source_height * scale)
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Center crop to target dimensions
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height

        cropped = resized.crop((left, top, right, bottom))

        return cropped

    async def _load_image(self, image_path: str) -> Image.Image:
        """
        Load image from path (supports both local files and URLs).
        Follows redirects for URLs like picsum.photos.
        """
        if image_path.startswith('http://') or image_path.startswith('https://'):
            # Download image with redirect following
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(image_path)
                response.raise_for_status()
                from io import BytesIO
                return Image.open(BytesIO(response.content))
        else:
            # Load from local file
            local_path = self.files_dir / image_path.lstrip('/static/')
            return Image.open(local_path)

    def _save_image(self, canvas: Image.Image, campaign_name: str, headline: str, filename: str) -> str:
        """
        Save final post image (Gemini-generated with logo and border).

        Path format: posts/{CampaignName}_{PostHeadline}/image_{aspectRatio}.png
        """
        # Sanitize campaign name and headline for filesystem
        safe_campaign = self._sanitize_filename(campaign_name)
        safe_headline = self._sanitize_filename(headline)[:50]  # Truncate to 50 chars

        # Create folder name
        folder_name = f"{safe_campaign}_{safe_headline}"
        output_dir = self.posts_dir / folder_name
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save image
        output_file = output_dir / filename
        canvas.save(output_file, 'PNG', quality=95)

        # Return relative path
        return f"posts/{folder_name}/{filename}"

    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize string for use in filename.
        Remove special characters, replace spaces with underscores.
        """
        # Remove special characters
        name = re.sub(r'[^\w\s-]', '', name)
        # Replace spaces with underscores
        name = re.sub(r'\s+', '_', name)
        # Remove consecutive underscores
        name = re.sub(r'_+', '_', name)
        return name.strip('_')
