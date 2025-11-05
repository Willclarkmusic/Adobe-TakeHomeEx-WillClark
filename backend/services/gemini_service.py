"""
Gemini AI Service for generating post copy and images.

Uses Google's Gemini API to generate professional social media post content
based on campaign and product information.
"""
import json
import re
import logging
import asyncio
import os
from typing import Dict, Optional
from google import genai
from google.genai import types
from PIL import Image
import io

from .config import get_settings

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

##################################################
# Global Variables
##################################################
DIMENSIONS_MAP = {
    "1:1": "1080x1080 pixels (square)",
    "16:9": "1920x1080 pixels (landscape)",
    "9:16": "1080x1920 pixels (vertical/story format)"
}

##################################################
# Prompt Templates
##################################################
COPYWRITER_SYSTEM_PROMPT = """You are a professional social media copywriter
    specializing in creative ad campaigns.

Generate compelling social media post content based on
    the following information:

CAMPAIGN INFORMATION:
- Campaign Message: {campaign_message}{cta_section}
- Target Region: {target_region}
- Target Audience: {target_audience}

PRODUCT INFORMATION:
- Product Name: {product_name}{desc_section}

USER REQUEST:
{user_prompt}

OUTPUT REQUIREMENTS:
Generate a JSON object with exactly three fields:
1. "headline": A short, punchy headline (max 60 characters)
    that grabs attention
2. "body_text": Main post content (2-3 sentences, max 280 characters)
    that highlights key benefits
3. "caption": An engaging social media caption (1-2 sentences,
    max 150 characters) with relevant tone

STYLE GUIDELINES:
- Match the tone to the target audience
- Match the primary language of the region unless specified otherwise or if
    region is Global use English
    - Here's the region: {target_region}
- Incorporate the campaign message naturally
- Make it platform-appropriate for Instagram/Facebook/LinkedIn
- Use active voice and compelling language
- Focus on benefits, not just features
- Keep it concise and impactful

IMPORTANT: Return ONLY a valid JSON object with no additional text
    or explanation. Format:
{{
"headline": "Your headline here",
"body_text": "Your body text here",
"caption": "Your caption here",
"text_color": "#RRGGBB"
}}

The "text_color" should be a hex color code for the headline background that:
- Complements the campaign/product vibe
- Provides high contrast for white text
- Is bold, vibrant, and eye-catching for social media
- Examples: "#FF4081" (hot pink), "#00BCD4" (cyan),
    "#FF6F00" (orange), "#8E24AA" (purple)"""

IMAGE_ADAPTATION_PROMPT = """Adapt this image to a new aspect ratio while
    maintaining the exact same visual style, and content.

TARGET FORMAT:
- Output size: exactly {dimensions}
- Aspect ratio: {aspect_ratio}

REQUIREMENTS:
- Keep the EXACT same product, styling, colors, atmosphere, and visual elements
- Keep the "{headline}" text in the same style and position relative to the
    new composition
- Intelligently extend or crop the composition to fit the new {aspect_ratio}
- If extending (adding more space), naturally continue the
    background/atmosphere as if the camera zoomed out
- If cropping (removing space), do so in a way that preserves the key elements
- Maintain visual consistency - this should look like the same image, just
    reformatted or zoomed out

Create a version of this image at {dimensions} that feels like a natural
    recomposition, not a distorted stretch or tiling."""

IMAGE_GENERATION_PROMPT = """Transform this product image for a social media
    marketing campaign while keeping the product clearly recognizable.

CAMPAIGN CONTEXT:
- Campaign Message: {campaign_message}
- Post Headline: {headline}
- Creative Direction: {user_prompt}

OUTPUT FORMAT:
- Generate the image at exactly {dimensions}
- Compose the image to perfectly fit the {aspect_ratio} aspect ratio without
    any stretching or distortion
- Fill the entire frame naturally and beautifully

REQUIREMENTS:
- Keep the product as the main focus and clearly identifiable
- Add campaign-appropriate atmosphere, lighting, and styling
- Enhance visual appeal for social media (vibrant, eye-catching)
- Make it feel professional and on-brand
- The style should complement the headline: "{headline}"
- Add the "{headline}" text as an overlay in a visually appealing way
    appropriate for the campaign
- Compose elements to naturally fill the {aspect_ratio} format

Transform the image to match the campaign vibe while maintaining product
clarity and the specified dimensions."""

MOOD_BOARD_SYSTEM_PROMPT = """You are creating inspirational creative material
for a social media campaign mood board.

CRITICAL RULES:
- DO NOT include any text, words, letters, or typography on the image
- DO NOT add captions, labels, or written content of any kind
- Focus purely on visual aesthetics, mood, atmosphere, and emotion
- Create cohesive compositions that blend the reference images naturally
- Emphasize lighting, color palette, and visual storytelling
- Generate professional, high-quality visuals suitable for brand campaigns

Your output should be a visually stunning image with NO TEXT whatsoever."""

MOOD_BOARD_FULL_PROMPT = """{system_prompt}

USER CREATIVE DIRECTION:
{prompt}

Generate a visually stunning mood board image that captures this
creative direction."""

VEO_VIDEO_SYSTEM_PROMPT = """Create inspirational video material for a social
media campaign mood board.

CRITICAL RULES:
- DO NOT include any text or typography on the video
- Create smooth, cinematic motion
- Maintain visual coherence throughout the video
- Focus on atmosphere, emotion, and visual storytelling
- Generate professional, high-quality video suitable for brand campaigns

Your output should be a visually stunning video with NO TEXT whatsoever."""

VEO_VIDEO_FULL_PROMPT = """{system_prompt}

USER CREATIVE DIRECTION:
{prompt}

Generate a cinematic video that captures this creative direction with smooth
motion and visual appeal."""

VEO_VIDEO_TECHNICAL_PROMPT = """{full_prompt}

TECHNICAL SPECIFICATIONS:
- Aspect Ratio: {aspect_ratio}
- Duration: {duration} seconds"""

PRODUCT_IMAGE_GENERATION_PROMPT = """Generate a professional product
    photograph for: {product_name}{desc_text}{style_text}

REQUIREMENTS:
- Create a clean, professional product photo suitable for e-commerce and
    social media
- Place the product as the main focal point with clear visibility
- Use appropriate lighting that highlights product features
- Professional composition with simple, complementary background
- High quality, photorealistic style
- The product should look appealing and ready for marketing use
- Output size: 1080x1080 pixels (square format)

IMPORTANT: Focus on creating a professional, marketable product image that
would work well in advertising campaigns."""


def _extract_image_from_response(
    response,
    return_bytes: bool = False,
    success_message: str = "Image extracted successfully"
):
    """
    Extract PIL Image or bytes from Gemini API response.
    """
    if not response.parts and not hasattr(response, 'image'):
        raise ValueError("No image data found in Gemini response")

    # Extract from response.parts
    generated_image = None
    if response.parts:
        for part in response.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                image_data = part.inline_data.data
                if return_bytes:
                    logger.info(f"  ✅ {success_message}")
                    generated_image = image_data
                else:
                    generated_image = Image.open(io.BytesIO(image_data))
                    logger.info(f"✅ {success_message}")
    # Fallback to response.image
    elif hasattr(response, 'image'):
        if return_bytes:
            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            response.image.save(img_byte_arr, format='PNG')
            logger.info(f"  ✅ {success_message}")
            generated_image = img_byte_arr.getvalue()
        else:
            logger.info(f"✅ {success_message}")
            generated_image = response.image

    return generated_image


class GeminiService:
    """
    Service for interacting with Google's Gemini API to generate post content.
    """

    def __init__(self, text_model_name='gemini-2.5-flash',
                 image_model_name='gemini-2.5-flash-image'):
        """
        Initialize the Gemini service with API configuration.
        """
        settings = get_settings()
        api_key = settings.GEMINI_API_KEY

        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError(
                "GEMINI_API_KEY not set in environment variables. "
                "Please add your API key to backend/.env file."
            )

        # Create client for new google-genai SDK
        self.client = genai.Client(api_key=api_key)

        # Model names for reference
        self.text_model_name = text_model_name
        self.image_model_name = image_model_name

    async def generate_post_copy(
        self,
        campaign_message: str,
        call_to_action: Optional[str],
        target_region: str,
        target_audience: str,
        product_name: str,
        product_description: Optional[str],
        user_prompt: str
    ) -> Dict[str, str]:
        """
        Generate post copy (headline, body_text, caption) using Gemini API.
        Returns:
            Dict with keys: headline, body_text, caption, text_color
        """
        cta_text = f"\n- Call to Action: {call_to_action}" if call_to_action else ""
        desc_text = f"\n- Product Description: {product_description}" if product_description else ""

        system_prompt = COPYWRITER_SYSTEM_PROMPT.format(
            campaign_message=campaign_message,
            cta_section=cta_text,
            target_region=target_region,
            target_audience=target_audience,
            product_name=product_name,
            desc_section=desc_text,
            user_prompt=user_prompt
        )
        try:
            # Generate Text Content With Gemini
            response = self.client.models.generate_content(
                model=self.text_model_name,
                contents=system_prompt
            )
            # Parse the response
            result = self.parse_gemini_response(response.text)

            return result

        except Exception as _:
            raise Exception(f"Failed to generate post copy: {str(_)}")

    def parse_gemini_response(self, response_text: str) -> Dict[str, str]:
        """
        Parse the Gemini API response and extract JSON content.
        """
        try:
            # Try to extract JSON from response
            # (handles cases where model adds extra text)
            json_match = re.search(r'\{[^}]*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
            else:
                # Try parsing the entire response as JSON
                data = json.loads(response_text)

            # Validate required fields
            required_fields = ["headline", "body_text", "caption", "text_color"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                raise ValueError(
                    f"Missing required fields: {', '.join(missing_fields)}")
            return {
                "headline": data["headline"].strip(),
                "body_text": data["body_text"].strip(),
                "caption": data["caption"].strip(),
                "text_color": data["text_color"].strip()
            }
        except json.JSONDecodeError as _:
            raise ValueError(
                f"Failed to parse JSON: {str(_)}\nResponse: {response_text}")
        except Exception as _:
            raise ValueError(f"Failed to parse Gemini response: {str(_)}")

    async def generate_product_image(
        self,
        product_image: Image.Image,
        campaign_message: str,
        headline: str,
        user_prompt: str,
        aspect_ratio: str = "1:1"
    ) -> Image.Image:
        """
        Generate a stylized product image using
        Gemini 2.5 Flash Image (img2img).
        """
        logger.info(f"Generating {aspect_ratio} image with Gemini 2.5 Flash Image...")

        # Build image generation prompt
        image_prompt = self._build_image_prompt(
            campaign_message=campaign_message,
            headline=headline,
            user_prompt=user_prompt,
            aspect_ratio=aspect_ratio
        )

        try:
            ##################################################
            # Generate New Post With Gemini
            ##################################################
            response = self.client.models.generate_content(
                model=self.image_model_name,
                contents=[image_prompt, product_image],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio
                    )
                )
            )

            # Extract generated image from response
            return _extract_image_from_response(
                response,
                return_bytes=False,
                success_message="Image generated successfully"
            )

        except Exception as _:
            logger.error(f"❌ Image generation failed: {str(_)}")
            raise Exception(f"Failed to generate product image: {str(_)}")

    async def generate_product_image_adaptation(
        self,
        base_image: Image.Image,
        headline: str,
        new_aspect_ratio: str
    ) -> Image.Image:
        """
        Adapt an existing generated image to a new aspect ratio.
        This ensures visual consistency across multiple aspect ratios
        by extending/adapting the same base image rather than generating
        completely new images.
        """
        logger.info(f"Adapting image to {new_aspect_ratio}...")

        # Build adaptation prompt
        adaptation_prompt = self._build_adaptation_prompt(
            headline, new_aspect_ratio)

        try:
            # Generate New Aspect Ratio With Gemini img2img
            response = self.client.models.generate_content(
                model=self.image_model_name,
                contents=[adaptation_prompt, base_image],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio=new_aspect_ratio
                    )
                )
            )

            # Extract adapted image from response
            return _extract_image_from_response(
                response,
                return_bytes=False,
                success_message="Image adapted successfully"
            )

        except Exception as _:
            logger.error(f"❌ Image adaptation failed: {str(_)}")
            raise Exception(f"Failed to adapt image: {str(_)}")

    def _build_adaptation_prompt(
        self,
        headline: str,
        aspect_ratio: str
    ) -> str:
        """
        Build a prompt for adapting an existing image to a new aspect ratio.
        """
        dimensions = DIMENSIONS_MAP.get(aspect_ratio, "1080x1080 pixels")

        prompt = IMAGE_ADAPTATION_PROMPT.format(
            dimensions=dimensions,
            aspect_ratio=aspect_ratio,
            headline=headline
        )
        return prompt

    def _build_image_prompt(
        self,
        campaign_message: str,
        headline: str,
        user_prompt: str,
        aspect_ratio: str = "1:1"
    ) -> str:
        """
        Build a detailed prompt for image generation that maintains product integrity
        while adding campaign-appropriate styling.
        """
        dimensions = DIMENSIONS_MAP.get(aspect_ratio, "1080x1080 pixels")
        prompt = IMAGE_GENERATION_PROMPT.format(
            campaign_message=campaign_message,
            headline=headline,
            user_prompt=user_prompt,
            dimensions=dimensions,
            aspect_ratio=aspect_ratio
        )
        return prompt

    async def generate_mood_image(
        self,
        prompt: str,
        source_images: list,
        aspect_ratio: str = "1:1"
    ) -> bytes:
        """
        Generate mood board image with Gemini 2.5 Flash Image.
        Creates inspirational creative material for mood boards without text overlays.
        """
        logger.info(f"Generating mood board image ({aspect_ratio}).")

        # Build mood board specific system prompt
        system_prompt = MOOD_BOARD_SYSTEM_PROMPT

        # Load source images as PIL Images
        image_parts = []
        failed_images = []

        for img_path in source_images:
            try:
                # Handle different path formats
                clean_path = img_path.lstrip('/')

                # Remove /static/ prefix if present
                if clean_path.startswith('static/'):
                    clean_path = clean_path[7:]  # Remove "static/"

                # Backend runs from backend/ dir, files are in ../files/
                possible_paths = [
                    f"../files/{clean_path}",
                    f"files/{clean_path}",
                    clean_path
                ]

                loaded = False
                for path in possible_paths:
                    if os.path.exists(path):
                        with Image.open(path) as img:
                            image_parts.append(img.copy())
                        logger.info(f"  ✓ Loaded source image: {img_path}")
                        loaded = True
                        break

                if not loaded:
                    logger.warning(f"  ⚠️ Could not find source image: {img_path}")
                    failed_images.append(img_path)
            except Exception as e:
                logger.warning(f"  ⚠️ Failed to load {img_path}: {str(e)}")
                failed_images.append(img_path)

        # If source images were provided but none could be loaded, fail
        if source_images and not image_parts:
            raise ValueError(
                f"Could not load any of the {len(source_images)} source images. "
                f"Generation aborted. Failed images: {', '.join(failed_images)}"
            )

        # Combine system prompt with user prompt
        full_prompt = MOOD_BOARD_FULL_PROMPT.format(
            system_prompt=system_prompt,
            prompt=prompt
        )

        try:
            # Generate with Gemini 2.5 Flash Image
            response = self.client.models.generate_content(
                model=self.image_model_name,
                contents=[full_prompt] + image_parts,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio
                    )
                )
            )

            # Extract generated image as bytes
            return _extract_image_from_response(
                response,
                return_bytes=True,
                success_message="Mood image generated successfully"
            )

        except Exception as _:
            logger.error(f"  ❌ Mood image generation failed: {str(_)}")
            raise Exception(f"Failed to generate mood image: {str(_)}")

    async def generate_product_image_from_text(
        self,
        product_name: str,
        product_description: Optional[str] = None,
        user_prompt: Optional[str] = None
    ) -> Image.Image:
        """
        Generate a product image from text description using img2img transformation.
        Since Gemini Flash Image doesn't support pure text-to-image, this method:
        1. Creates a neutral gray base template (1080x1080)
        2. Uses img2img to transform it into a professional product photo
        """
        logger.info(f"Generating product image from text: {product_name}")
        try:
            # Step 1: Create neutral base template
            base_size = (1080, 1080)
            base_color = '#f5f5f5'  # Light gray background
            base_template = Image.new('RGB', base_size, color=base_color)
            logger.info(f"   Created base template: {base_size}")

            # Step 2: Build detailed prompt from product information
            desc_text = f"\n\nProduct Description: {product_description}" if product_description else ""
            style_text = f"\n\nStyle/Mood: {user_prompt}" if user_prompt else ""

            generation_prompt = PRODUCT_IMAGE_GENERATION_PROMPT.format(
                product_name=product_name,
                desc_text=desc_text,
                style_text=style_text
            )

            # Step 3: Use img2img to transform template into product photo
            response = self.client.models.generate_content(
                model=self.image_model_name,
                contents=[generation_prompt, base_template],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio="1:1"
                    )
                )
            )

            # Step 4: Extract generated image from response
            generated_image = _extract_image_from_response(
                response,
                return_bytes=False,
                success_message="Product image generated!"
            )
            return generated_image

        except Exception as _:
            logger.error(f"   ❌ Product image generation failed: {str(_)}")
            raise Exception(f"Failed to generate product image from text: {str(_)}")

    async def generate_veo_video(
        self,
        prompt: str,
        source_images: list,
        aspect_ratio: str = "16:9",
        duration: int = 6
    ) -> bytes:
        """
        Generate mood board video with Veo (async with polling).
        Creates inspirational video material for mood boards.
        """
        logger.info(f"🎬 Generating mood board video with Veo ({aspect_ratio}, {duration}s)...")

        # Build mood board specific system prompt for video
        system_prompt = VEO_VIDEO_SYSTEM_PROMPT

        # Combine system prompt with user prompt
        full_prompt = VEO_VIDEO_FULL_PROMPT.format(
            system_prompt=system_prompt,
            prompt=prompt
        )

        try:
            # Start video generation (async operation)
            logger.info("Starting Veo generation (this may take 30-60 seconds)...")

            # Veo 3.1 model name (standard version supports reference images)
            veo_model = "veo-3.1-generate-preview"

            # Build prompt with technical specifications
            enhanced_prompt = VEO_VIDEO_TECHNICAL_PROMPT.format(
                full_prompt=full_prompt,
                aspect_ratio=aspect_ratio,
                duration=duration
            )

            # Load single reference image (0 or 1 only)
            reference_image = None

            if source_images and len(source_images) > 0:
                img_path = source_images[0]  # Take only the first image
                logger.info(f"  📸 Loading reference image: {img_path}")

                try:
                    # Handle different path formats
                    clean_path = img_path.lstrip('/')
                    if clean_path.startswith('static/'):
                        clean_path = clean_path[7:]  # Remove "static/"

                    # Try different possible locations
                    possible_paths = [
                        f"../files/{clean_path}",
                        f"files/{clean_path}",
                        clean_path
                    ]

                    file_path = None
                    for path in possible_paths:
                        if os.path.exists(path):
                            file_path = path
                            break

                    if not file_path:
                        logger.error(f"  ❌ Reference image not found: {img_path}")
                        raise ValueError(f"Reference image not found: {img_path}. Aborting video generation.")

                    # Load as PIL Image (like the example: image.generated_images[0].image)
                    reference_image = Image.open(file_path)

                    # Convert to RGB if it's RGBA (PNG with transparency)
                    if reference_image.mode == 'RGBA':
                        logger.info("  Converting RGBA to RGB...")
                        # Create white background
                        rgb_image = Image.new('RGB', reference_image.size,
                                              (255, 255, 255))
                        # Use alpha channel as mask
                        rgb_image.paste(reference_image,
                                        mask=reference_image.split()[3])
                        reference_image = rgb_image

                    logger.info(f"Loaded reference image: {img_path} (size: {reference_image.size}, mode: {reference_image.mode})")

                except Exception as _:
                    logger.error(f"❌ Failed to load reference image: {str(_)}")
                    raise ValueError(
                        f"Failed to load reference image: {str(_)}. Video generation aborted.")

            if reference_image:
                logger.info("Calling Veo API with 1 reference image...")

                # Ensure PIL Image is fully loaded into memory
                reference_image.load()

                # Wrap in VideoGenerationReferenceImage (like the multi-image example)
                ref_image = types.VideoGenerationReferenceImage(
                    image=reference_image,
                    reference_type="asset"
                )

                operation = self.client.models.generate_videos(
                    model=veo_model,
                    prompt=enhanced_prompt,
                    config=types.GenerateVideosConfig(
                        reference_images=[ref_image],  # Single image in list
                        aspect_ratio=aspect_ratio,
                    )
                )
            else:
                logger.info("  🎬 Calling Veo API (prompt-only, no reference image)...")
                operation = self.client.models.generate_videos(
                    model=veo_model,
                    prompt=enhanced_prompt,
                    config=types.GenerateVideosConfig(
                        aspect_ratio=aspect_ratio,
                    )
                )

            logger.info("  ⏳ Polling for video generation completion...")

            # Poll until complete
            max_attempts = 120  # 10 minutes max (120 * 5s)
            attempts = 0

            while not operation.done:
                await asyncio.sleep(5)  # Check every 5 seconds
                attempts += 1

                # Refresh operation status
                operation = self.client.operations.get(operation)

                if attempts % 6 == 0:  # Log every 30 seconds
                    logger.info(f"  Still generating... ({attempts * 5}s elapsed)")

                if attempts >= max_attempts:
                    raise TimeoutError("Video generation timed out after 10 minutes")

            logger.info("✅ Video generation complete!")

            # Download the video
            video = operation.response.generated_videos[0]
            video_data = self.client.files.download(file=video.video)
            return video_data

        except Exception as _:
            logger.error(f"❌ Video generation failed: {str(_)}")
            raise Exception(f"Failed to generate mood video: {str(_)}")
