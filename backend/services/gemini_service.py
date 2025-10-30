"""
Gemini AI Service for generating post copy.

Uses Google's Gemini API to generate professional social media post content
based on campaign and product information.
"""
import os
import json
import re
from typing import Dict, Optional
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()


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

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

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
            # Generate content using Gemini
            response = self.model.generate_content(system_prompt)

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
  "caption": "Your caption here"
}}"""

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
            required_fields = ["headline", "body_text", "caption"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

            return {
                "headline": data["headline"].strip(),
                "body_text": data["body_text"].strip(),
                "caption": data["caption"].strip()
            }

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}\nResponse: {response_text}")
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini response: {str(e)}")
