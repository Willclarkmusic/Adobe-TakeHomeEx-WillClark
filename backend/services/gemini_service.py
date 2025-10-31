"""
Gemini AI Service for generating post copy and images.

Uses Google's Gemini API to generate professional social media post content
based on campaign and product information.
"""
import os
import json
import re
import logging
from typing import Dict, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class GeminiService:
    """
    Service for interacting with Google's Gemini API to generate post content.
    """

    def __init__(self):
        """
        Initialize the Gemini service with API configuration.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError(
                "GEMINI_API_KEY not set in environment variables. "
                "Please add your API key to backend/.env file."
            )

        # Create client for new google-genai SDK
        self.client = genai.Client(api_key=api_key)

        # Model names for reference
        self.text_model_name = 'gemini-2.5-flash'
        self.image_model_name = 'gemini-2.5-flash-image'

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

        Args:
            campaign_message: The main campaign message
            call_to_action: Campaign CTA
            target_region: Target geographic region
            target_audience: Target audience description
            product_name: Name of the product
            product_description: Product description
            user_prompt: User's custom generation prompt

        Returns:
            Dict with keys: headline, body_text, caption

        Raises:
            Exception: If API call fails or response parsing fails
        """
        system_prompt = self.build_system_prompt(
            campaign_message=campaign_message,
            call_to_action=call_to_action,
            target_region=target_region,
            target_audience=target_audience,
            product_name=product_name,
            product_description=product_description,
            user_prompt=user_prompt
        )

        try:
            # Generate content using Gemini with new SDK
            response = self.client.models.generate_content(
                model=self.text_model_name,
                contents=system_prompt
            )

            # Parse the response
            result = self.parse_gemini_response(response.text)

            return result

        except Exception as e:
            raise Exception(f"Failed to generate post copy: {str(e)}")

    def build_system_prompt(
        self,
        campaign_message: str,
        call_to_action: Optional[str],
        target_region: str,
        target_audience: str,
        product_name: str,
        product_description: Optional[str],
        user_prompt: str
    ) -> str:
        """
        Build a comprehensive system prompt for professional copywriting.

        Returns:
            A formatted prompt string for Gemini
        """
        cta_section = f"\n- Call to Action: {call_to_action}" if call_to_action else ""
        desc_section = f"\n- Product Description: {product_description}" if product_description else ""

        prompt = f"""You are a professional social media copywriter specializing in creative ad campaigns.

Generate compelling social media post content based on the following information:

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
1. "headline": A short, punchy headline (max 60 characters) that grabs attention
2. "body_text": Main post content (2-3 sentences, max 280 characters) that highlights key benefits
3. "caption": An engaging social media caption (1-2 sentences, max 150 characters) with relevant tone

STYLE GUIDELINES:
- Match the tone to the target audience
- Incorporate the campaign message naturally
- Make it platform-appropriate for Instagram/Facebook/LinkedIn
- Use active voice and compelling language
- Focus on benefits, not just features
- Keep it concise and impactful

IMPORTANT: Return ONLY a valid JSON object with no additional text or explanation. Format:
{{
  "headline": "Your headline here",
  "body_text": "Your body text here",
  "caption": "Your caption here",
  "text_color": "#RRGGBB"
}}

The "text_color" field should be a hex color code for the headline background that:
- Complements the campaign/product vibe
- Provides high contrast for white text
- Is bold, vibrant, and eye-catching for social media
- Examples: "#FF4081" (hot pink), "#00BCD4" (cyan), "#FF6F00" (orange), "#8E24AA" (purple)"""

        return prompt

    def parse_gemini_response(self, response_text: str) -> Dict[str, str]:
        """
        Parse the Gemini API response and extract JSON content.

        Args:
            response_text: Raw response text from Gemini

        Returns:
            Dict with headline, body_text, and caption

        Raises:
            ValueError: If response cannot be parsed or is missing required fields
        """
        try:
            # Try to extract JSON from response (handles cases where model adds extra text)
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
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
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

            return {
                "headline": data["headline"].strip(),
                "body_text": data["body_text"].strip(),
                "caption": data["caption"].strip(),
                "text_color": data["text_color"].strip()
            }

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {response_text}")
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini response: {str(e)}")

    async def generate_product_image(
        self,
        product_image: Image.Image,
        campaign_message: str,
        headline: str,
        user_prompt: str,
        aspect_ratio: str = "1:1"
    ) -> Image.Image:
        """
        Generate a stylized product image using Gemini 2.5 Flash Image (img2img).

        Args:
            product_image: PIL Image of the product
            campaign_message: Campaign message for context
            headline: Generated headline to inform the image style
            user_prompt: User's custom generation prompt
            aspect_ratio: Desired aspect ratio ("1:1", "16:9", or "9:16")

        Returns:
            PIL Image of the generated/edited product image

        Raises:
            Exception: If image generation fails
        """
        logger.info(f"         🎨 Generating image with Gemini 2.5 Flash Image...")
        logger.info(f"         📐 Aspect ratio: {aspect_ratio}")

        # Build image generation prompt
        image_prompt = self._build_image_prompt(
            campaign_message=campaign_message,
            headline=headline,
            user_prompt=user_prompt,
            aspect_ratio=aspect_ratio
        )
        logger.info(f"         📝 Image prompt: {image_prompt[:100]}...")

        try:
            # Generate image using Gemini with img2img and aspect ratio config (new SDK)
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
            if response.parts:
                for part in response.parts:
                    # Check if this part contains image data
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # Convert inline_data to PIL Image
                        image_data = part.inline_data.data
                        generated_image = Image.open(io.BytesIO(image_data))
                        logger.info(f"         ✅ Image generated successfully! Size: {generated_image.size}")
                        return generated_image

            # If no image found in parts, try alternative access
            if hasattr(response, 'image'):
                logger.info(f"         ✅ Image generated successfully (via response.image)")
                return response.image

            raise ValueError("No image data found in Gemini response")

        except Exception as e:
            logger.error(f"         ❌ Image generation failed: {str(e)}")
            raise Exception(f"Failed to generate product image: {str(e)}")

    async def generate_product_image_adaptation(
        self,
        base_image: Image.Image,
        headline: str,
        new_aspect_ratio: str
    ) -> Image.Image:
        """
        Adapt an existing generated image to a new aspect ratio.

        This ensures visual consistency across multiple aspect ratios by extending/adapting
        the same base image rather than generating completely new images.

        Args:
            base_image: PIL Image that was already generated for one aspect ratio
            headline: The headline text (should already be on the image)
            new_aspect_ratio: Target aspect ratio ("1:1", "16:9", or "9:16")

        Returns:
            PIL Image adapted to the new aspect ratio

        Raises:
            Exception: If image adaptation fails
        """
        logger.info(f"         🔄 Adapting image to {new_aspect_ratio}...")
        logger.info(f"         📐 Source image size: {base_image.size}")

        # Build adaptation prompt
        adaptation_prompt = self._build_adaptation_prompt(headline, new_aspect_ratio)
        logger.info(f"         📝 Adaptation prompt: {adaptation_prompt[:100]}...")

        ##################################################
        # Generate With Gemini
        ##################################################
        try:
            # Adapt image using Gemini with img2img and aspect ratio config (new SDK)
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
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        adapted_image = Image.open(io.BytesIO(image_data))
                        logger.info(f"         ✅ Image adapted successfully! Size: {adapted_image.size}")
                        return adapted_image

            if hasattr(response, 'image'):
                logger.info(f"         ✅ Image adapted successfully (via response.image)")
                return response.image

            raise ValueError("No image data found in Gemini response")

        except Exception as e:
            logger.error(f"         ❌ Image adaptation failed: {str(e)}")
            raise Exception(f"Failed to adapt image to {new_aspect_ratio}: {str(e)}")

    def _build_adaptation_prompt(
        self,
        headline: str,
        aspect_ratio: str
    ) -> str:
        """
        Build a prompt for adapting an existing image to a new aspect ratio.
        """
        dimensions_map = {
            "1:1": "1080x1080 pixels (square)",
            "16:9": "1920x1080 pixels (landscape)",
            "9:16": "1080x1920 pixels (vertical/story format)"
        }
        dimensions = dimensions_map.get(aspect_ratio, "1080x1080 pixels")

        prompt = f"""Adapt this image to a new aspect ratio while maintaining the exact same visual style, and content.

TARGET FORMAT:
- Output size: exactly {dimensions}
- Aspect ratio: {aspect_ratio}

REQUIREMENTS:
- Keep the EXACT same product, styling, colors, atmosphere, and visual elements
- Keep the "{headline}" text in the same style and position relative to the new composition
- Intelligently extend or crop the composition to fit the new {aspect_ratio}
- If extending (adding more space), naturally continue the background/atmosphere as if the camera zoomed out
- If cropping (removing space), do so in a way that preserves the key elements
- Maintain visual consistency - this should look like the same image, just reformatted or zoomed out

Create a version of this image at {dimensions} that feels like a natural recomposition, not a distorted stretch or tiling."""

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
        # Map aspect ratios to exact dimensions
        dimensions_map = {
            "1:1": "1080x1080 pixels (square)",
            "16:9": "1920x1080 pixels (landscape)",
            "9:16": "1080x1920 pixels (vertical/story format)"
        }
        dimensions = dimensions_map.get(aspect_ratio, "1080x1080 pixels")

        prompt = f"""Transform this product image for a social media marketing campaign while keeping the product clearly recognizable.

CAMPAIGN CONTEXT:
- Campaign Message: {campaign_message}
- Post Headline: {headline}
- Creative Direction: {user_prompt}

OUTPUT FORMAT:
- Generate the image at exactly {dimensions}
- Compose the image to perfectly fit the {aspect_ratio} aspect ratio without any stretching or distortion
- Fill the entire frame naturally and beautifully

REQUIREMENTS:
- Keep the product as the main focus and clearly identifiable
- Add campaign-appropriate atmosphere, lighting, and styling
- Enhance visual appeal for social media (vibrant, eye-catching)
- Make it feel professional and on-brand
- The style should complement the headline: "{headline}"
- Add the "{headline}" text as an overlay in a visually appealing way appropriate for the campaign
- Compose elements to naturally fill the {aspect_ratio} format

Transform the image to match the campaign vibe while maintaining product clarity and the specified dimensions."""

        return prompt
