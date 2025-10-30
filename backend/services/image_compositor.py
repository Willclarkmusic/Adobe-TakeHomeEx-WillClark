"""
Image Compositing Service for generating social media post images.

Uses PIL/Pillow to composite product images, brand elements, and text overlays
into professionally designed post images for multiple aspect ratios.
"""
import os
import re
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import httpx


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

    # Font sizes for different elements and aspect ratios
    FONT_SIZES = {
        "1:1": {"headline": 64, "caption": 36},
        "16:9": {"headline": 72, "caption": 40},
        "9:16": {"headline": 56, "caption": 32}
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
        product_image_path: Optional[str],
        brand_images: List[str],
        headline: str,
        caption: str,
        campaign_name: str,
        output_filename: str
    ) -> str:
        """
        Create a post image with product, brand elements, and text overlays.

        Args:
            aspect_ratio: One of "1:1", "16:9", "9:16"
            product_image_path: Path to product image (can be None)
            brand_images: List of paths to brand images
            headline: Post headline text
            caption: Post caption text
            campaign_name: Campaign name for folder organization
            output_filename: Filename for the output image (e.g., "image_1-1.png")

        Returns:
            Relative path to the created image (e.g., "posts/CampaignName_Headline/image_1-1.png")
        """
        if aspect_ratio not in self.CANVAS_SIZES:
            raise ValueError(f"Invalid aspect ratio: {aspect_ratio}. Must be one of {list(self.CANVAS_SIZES.keys())}")

        # Get canvas size
        canvas_width, canvas_height = self.CANVAS_SIZES[aspect_ratio]

        # Create canvas with white background
        canvas = Image.new('RGB', (canvas_width, canvas_height), color='white')

        # Add product image if provided
        if product_image_path:
            canvas = await self._add_product_image(canvas, product_image_path, aspect_ratio)

        # Add brand logo overlay
        if brand_images:
            canvas = await self._add_brand_overlay(canvas, brand_images[0], aspect_ratio)

        # Add text overlays
        canvas = self._add_text_overlays(canvas, headline, caption, aspect_ratio)

        # Add border for neo-brutalist aesthetic
        canvas = self._add_border(canvas)

        # Save image
        output_path = self._save_image(canvas, campaign_name, headline, output_filename)

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

    def _add_text_overlays(self, canvas: Image.Image, headline: str, caption: str, aspect_ratio: str) -> Image.Image:
        """
        Add text overlays (headline and caption) to the canvas.
        """
        draw = ImageDraw.Draw(canvas)
        canvas_width, canvas_height = canvas.size

        # Get font sizes for this aspect ratio
        font_sizes = self.FONT_SIZES[aspect_ratio]

        try:
            # Try to use a nice sans-serif font (will fall back to default if not available)
            headline_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_sizes["headline"])
            caption_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_sizes["caption"])
        except:
            # Fallback to default font
            headline_font = ImageFont.load_default()
            caption_font = ImageFont.load_default()

        if aspect_ratio == "1:1":
            # Text at bottom
            self._draw_text_with_background(
                draw, headline, headline_font,
                x=canvas_width // 2,
                y=int(canvas_height * 0.8),
                canvas_width=canvas_width
            )
            self._draw_text_with_background(
                draw, caption, caption_font,
                x=canvas_width // 2,
                y=int(canvas_height * 0.9),
                canvas_width=canvas_width,
                bg_color=(255, 255, 255)
            )

        elif aspect_ratio == "16:9":
            # Text on right side
            text_x = int(canvas_width * 0.65)
            self._draw_text_with_background(
                draw, headline, headline_font,
                x=text_x,
                y=int(canvas_height * 0.4),
                canvas_width=int(canvas_width * 0.3)
            )
            self._draw_text_with_background(
                draw, caption, caption_font,
                x=text_x,
                y=int(canvas_height * 0.6),
                canvas_width=int(canvas_width * 0.3),
                bg_color=(255, 255, 255)
            )

        else:  # 9:16
            # Text in bottom third
            self._draw_text_with_background(
                draw, headline, headline_font,
                x=canvas_width // 2,
                y=int(canvas_height * 0.75),
                canvas_width=canvas_width
            )
            self._draw_text_with_background(
                draw, caption, caption_font,
                x=canvas_width // 2,
                y=int(canvas_height * 0.85),
                canvas_width=canvas_width,
                bg_color=(255, 255, 255)
            )

        return canvas

    def _draw_text_with_background(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.FreeTypeFont,
        x: int,
        y: int,
        canvas_width: int,
        bg_color: Tuple[int, int, int] = (0, 0, 0)
    ):
        """
        Draw text with a colored background box for better readability.
        """
        # Wrap text to fit width
        wrapped_text = self._wrap_text(text, font, canvas_width - 40)

        # Get text bounding box
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Draw background rectangle
        padding = 20
        bg_x1 = x - text_width // 2 - padding
        bg_y1 = y - text_height // 2 - padding
        bg_x2 = x + text_width // 2 + padding
        bg_y2 = y + text_height // 2 + padding

        draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=bg_color, outline=(0, 0, 0), width=3)

        # Draw text
        text_color = (255, 255, 255) if bg_color == (0, 0, 0) else (0, 0, 0)
        draw.text((x, y), wrapped_text, font=font, fill=text_color, anchor="mm", align="center")

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
        """
        if image_path.startswith('http://') or image_path.startswith('https://'):
            # Download image
            async with httpx.AsyncClient() as client:
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
