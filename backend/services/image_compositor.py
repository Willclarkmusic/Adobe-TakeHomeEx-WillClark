"""
Image Compositing Service for generating social media post images.

Uses PIL/Pillow to composite product images, brand elements, and text overlays
into professionally designed post images for multiple aspect ratios.
"""
import os
import re
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
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

    # Font sizes for HUGE, eye-catching headlines
    FONT_SIZES = {
        "1:1": {"headline": 120},      # Massive for square posts
        "16:9": {"headline": 100},     # Big for landscape
        "9:16": {"headline": 140}      # Huge for vertical/stories
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
        brand_images: List[str],
        headline: str,
        text_color: str,
        campaign_name: str,
        output_filename: str
    ) -> str:
        """
        Create a post image by adding headline overlay to Gemini-generated image.

        Args:
            aspect_ratio: One of "1:1", "16:9", "9:16"
            generated_image: PIL Image from Gemini (already stylized)
            brand_images: List of paths to brand images
            headline: Post headline text (HUGE, stylized)
            text_color: Hex color code for headline background (e.g., "#FF4081")
            campaign_name: Campaign name for folder organization
            output_filename: Filename for the output image (e.g., "image_1-1.png")

        Returns:
            Relative path to the created image (e.g., "posts/CampaignName_Headline/image_1-1.png")
        """
        if aspect_ratio not in self.CANVAS_SIZES:
            raise ValueError(f"Invalid aspect ratio: {aspect_ratio}. Must be one of {list(self.CANVAS_SIZES.keys())}")

        # Get canvas size
        canvas_width, canvas_height = self.CANVAS_SIZES[aspect_ratio]
        logger.info(f"      📐 Target size: {canvas_width}x{canvas_height}")

        # Use Gemini-generated image as the base, or create white canvas
        if generated_image:
            logger.info(f"      🖼️  Using Gemini-generated image as base ({generated_image.size})")
            # Resize generated image to match canvas size
            canvas = generated_image.resize((canvas_width, canvas_height), Image.Resampling.LANCZOS)
            logger.info(f"      ✅ Gemini image resized to canvas size")
        else:
            logger.info(f"      ⚠️  No generated image, creating white canvas")
            canvas = Image.new('RGB', (canvas_width, canvas_height), color='white')

        # Add brand logo overlay
        if brand_images:
            logger.info(f"      🏷️  Adding brand logo overlay from: {brand_images[0]}")
            canvas = await self._add_brand_overlay(canvas, brand_images[0], aspect_ratio)
            logger.info(f"      ✅ Brand logo added")
        else:
            logger.info(f"      ⚠️  No brand images provided")

        # Add HUGE stylized headline overlay (caption not included on image)
        logger.info(f"      💬 Adding HUGE stylized headline: '{headline}'")
        logger.info(f"      🎨 Using background color: {text_color}")
        canvas = self._add_headline_overlay(canvas, headline, text_color, aspect_ratio)
        logger.info(f"      ✅ Headline overlay composited onto image!")

        # Add border for neo-brutalist aesthetic
        canvas = self._add_border(canvas)
        logger.info(f"      🖼️  Neo-brutalist border added")

        # Save image
        logger.info(f"      💾 Saving final composited image...")
        output_path = self._save_image(canvas, campaign_name, headline, output_filename)
        logger.info(f"      ✅ Image saved to: {output_path}")

        return output_path

    async def _add_product_image(self, canvas: Image.Image, product_path: str, aspect_ratio: str) -> Image.Image:
        """
        Add product image to canvas based on aspect ratio template.
        """
        try:
            # Load product image
            product_img = await self._load_image(product_path)

            canvas_width, canvas_height = canvas.size

            if aspect_ratio == "1:1":
                # Center product in top 60% of canvas
                product_img = self._resize_to_fit(product_img, int(canvas_width * 0.8), int(canvas_height * 0.6))
                x = (canvas_width - product_img.width) // 2
                y = int(canvas_height * 0.1)

            elif aspect_ratio == "16:9":
                # Place product on left side
                product_img = self._resize_to_fit(product_img, int(canvas_width * 0.45), int(canvas_height * 0.7))
                x = int(canvas_width * 0.05)
                y = (canvas_height - product_img.height) // 2

            else:  # 9:16
                # Place product in top 60%
                product_img = self._resize_to_fit(product_img, int(canvas_width * 0.85), int(canvas_height * 0.5))
                x = (canvas_width - product_img.width) // 2
                y = int(canvas_height * 0.1)

            # Paste product image
            canvas.paste(product_img, (x, y), product_img if product_img.mode == 'RGBA' else None)

            return canvas

        except Exception as e:
            print(f"Warning: Failed to add product image: {e}")
            return canvas

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

    def _add_headline_overlay(self, canvas: Image.Image, headline: str, text_color: str, aspect_ratio: str) -> Image.Image:
        """
        Add HUGE, stylized headline overlay to the canvas.
        Only headline is composited - caption stays in DB only.
        """
        draw = ImageDraw.Draw(canvas)
        canvas_width, canvas_height = canvas.size

        # Get HUGE font size for this aspect ratio
        font_size = self.FONT_SIZES[aspect_ratio]["headline"]
        logger.info(f"         🔤 Font size: {font_size}px")

        # Try multiple font paths
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
            "DejaVuSans-Bold.ttf",  # Try without path
        ]

        headline_font = None
        for font_path in font_paths:
            try:
                headline_font = ImageFont.truetype(font_path, font_size)
                logger.info(f"         ✅ Loaded font: {font_path}")
                break
            except Exception as e:
                logger.info(f"         ⚠️  Failed to load {font_path}: {e}")
                continue

        if headline_font is None:
            # Last resort: use default font (will be tiny)
            logger.error(f"         ❌ ALL FONTS FAILED! Using default (will be tiny)")
            headline_font = ImageFont.load_default()

        # Parse hex color (with fallback to hot pink)
        try:
            bg_color = tuple(int(text_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            logger.info(f"         🎨 Parsed color: RGB{bg_color}")
        except:
            bg_color = (255, 64, 129)  # Default hot pink #FF4081
            logger.info(f"         ⚠️  Using default hot pink color")

        logger.info(f"         📏 Canvas dimensions: {canvas_width}x{canvas_height}")

        # Position headline based on aspect ratio
        if aspect_ratio == "1:1":
            # Bottom of square post
            self._draw_stylized_headline(
                draw, headline, headline_font,
                x=canvas_width // 2,
                y=int(canvas_height * 0.85),
                canvas_width=int(canvas_width * 0.9),
                bg_color=bg_color
            )

        elif aspect_ratio == "16:9":
            # Right side for landscape
            text_x = int(canvas_width * 0.70)
            self._draw_stylized_headline(
                draw, headline, headline_font,
                x=text_x,
                y=int(canvas_height * 0.5),
                canvas_width=int(canvas_width * 0.25),
                bg_color=bg_color
            )

        else:  # 9:16
            # Bottom third for vertical/story
            self._draw_stylized_headline(
                draw, headline, headline_font,
                x=canvas_width // 2,
                y=int(canvas_height * 0.80),
                canvas_width=int(canvas_width * 0.85),
                bg_color=bg_color
            )

        return canvas

    def _draw_stylized_headline(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.FreeTypeFont,
        x: int,
        y: int,
        canvas_width: int,
        bg_color: Tuple[int, int, int]
    ):
        """
        Draw HUGE stylized headline with vibrant colored background and bold border.
        Super eye-catching for social media!
        """
        logger.info(f"         ✏️  Drawing text at position ({x}, {y})")

        # Wrap text to fit width
        wrapped_text = self._wrap_text(text, font, canvas_width - 60)
        logger.info(f"         📝 Text wrapped to: '{wrapped_text}'")

        # Get text bounding box
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        logger.info(f"         📐 Text box size: {text_width}x{text_height}")

        # HUGE padding for impact
        padding = 40
        bg_x1 = x - text_width // 2 - padding
        bg_y1 = y - text_height // 2 - padding
        bg_x2 = x + text_width // 2 + padding
        bg_y2 = y + text_height // 2 + padding

        # Draw thick black border for neo-brutalist style
        border_width = 8
        draw.rectangle(
            [bg_x1 - border_width, bg_y1 - border_width, bg_x2 + border_width, bg_y2 + border_width],
            fill=(0, 0, 0)
        )
        logger.info(f"         ⬛ Black border drawn (8px)")

        # Draw vibrant colored background
        draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=bg_color)
        logger.info(f"         🟦 Colored background drawn RGB{bg_color}")

        # Draw white text for maximum contrast
        draw.text((x, y), wrapped_text, font=font, fill=(255, 255, 255), anchor="mm", align="center", stroke_width=2, stroke_fill=(0, 0, 0))
        logger.info(f"         ✅ WHITE TEXT DRAWN! (with black stroke)")

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
        """
        Wrap text to fit within max_width.
        """
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            current_line.append(word)
            line = ' '.join(current_line)
            bbox = font.getbbox(line)
            if bbox[2] - bbox[0] > max_width:
                if len(current_line) == 1:
                    # Single word is too long, just use it
                    lines.append(current_line.pop())
                else:
                    # Remove last word and start new line
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return '\n'.join(lines)

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
        Save image to structured path and return relative path.

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
