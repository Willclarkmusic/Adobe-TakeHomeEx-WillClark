"""
Ayrshare Service for social media posting and scheduling.

Handles interaction with Ayrshare API for:
- Retrieving connected social media profiles
- Posting immediately
- Scheduling posts for future dates
- Creating recurring posts with Auto Repost
- Canceling scheduled posts
"""
import os
import logging
import httpx
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

AYRSHARE_API_KEY = os.getenv("AYRSHARE_API_KEY")
AYRSHARE_BASE_URL = "https://app.ayrshare.com/api"


class AyrshareService:
    """
    Service for interacting with Ayrshare API.
    """

    def __init__(self):
        """Initialize Ayrshare service with API key."""
        if not AYRSHARE_API_KEY:
            raise ValueError("AYRSHARE_API_KEY not found in environment variables")

        # Strip whitespace and quotes that might be in .env file
        self.api_key = AYRSHARE_API_KEY.strip().strip('"').strip("'")
        self.base_url = AYRSHARE_BASE_URL

        # Debug: Log API key (first/last 4 chars only for security)
        if len(self.api_key) > 8:
            logger.info(f"  🔑 Using API Key: {self.api_key[:4]}...{self.api_key[-4:]} (length: {len(self.api_key)})")
        else:
            logger.warning(f"  ⚠️ API Key seems too short: {len(self.api_key)} chars - '{self.api_key}'")

        # Ayrshare uses Bearer authentication
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def get_profiles(self) -> List[Dict[str, Any]]:
        """
        Get all connected social media profiles from Ayrshare.

        Returns:
            List of profile dictionaries with platform, username, etc.

        Raises:
            httpx.HTTPError: If API request fails
        """
        logger.info("📱 Fetching connected profiles from Ayrshare...")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/user",
                    headers=self.headers,
                    timeout=30.0
                )

                # Log response details for debugging
                logger.info(f"  Response Status: {response.status_code}")

                if response.status_code == 403:
                    # Log the error response body
                    error_body = response.text
                    logger.error(f"  403 Error Response: {error_body}")
                    raise httpx.HTTPStatusError(
                        f"Authentication failed. Check your API key. Response: {error_body}",
                        request=response.request,
                        response=response
                    )

                response.raise_for_status()
                data = response.json()
                logger.info(f"  ✓ API call successful")

            except httpx.HTTPStatusError as e:
                logger.error(f"  HTTP Error: {e}")
                raise
            except Exception as e:
                logger.error(f"  Unexpected error: {e}")
                raise

        # Ayrshare returns profiles in data.displayNames (list of profile objects)
        # activeSocialAccounts is just a list of platform names ['twitter', 'facebook', etc]
        profiles = data.get("displayNames", [])
        logger.info(f"  ✓ Found {len(profiles)} connected profiles")

        # Transform to our format
        transformed_profiles = []
        for profile in profiles:
            transformed_profiles.append({
                "profile_key": profile.get("id", ""),
                "platform": profile.get("platform", "unknown").lower(),
                "username": profile.get("username", ""),
                "display_name": profile.get("displayName", ""),
                "is_active": True  # All profiles in displayNames are active
            })

        logger.info(f"  ✓ Transformed {len(transformed_profiles)} profiles")
        return transformed_profiles

    async def post_immediate(
        self,
        post_text: str,
        platforms: List[str],
        media_urls: List[str] = None
    ) -> Dict[str, Any]:
        """
        Post content immediately to social media (actually ~10 seconds from now).

        Args:
            post_text: Text content for the post
            platforms: List of platform names (e.g., ["instagram", "facebook"])
            media_urls: List of public image URLs (optional)

        Returns:
            Ayrshare API response with post ID and status

        Raises:
            httpx.HTTPError: If API request fails
        """
        logger.info(f"📤 Posting immediately to {platforms}...")

        # Schedule 10 seconds from now to ensure processing time
        schedule_time = datetime.utcnow() + timedelta(seconds=10)

        payload = {
            "post": post_text,
            "platforms": platforms,
            "scheduleDate": schedule_time.isoformat() + "Z"
        }

        if media_urls:
            payload["mediaUrls"] = media_urls

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/post",
                headers=self.headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()

        logger.info(f"  ✅ Posted successfully: {data.get('id', 'N/A')}")
        return data

    async def post_scheduled(
        self,
        post_text: str,
        platforms: List[str],
        schedule_time: datetime,
        media_urls: List[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule a post for a specific future date/time.

        Args:
            post_text: Text content for the post
            platforms: List of platform names
            schedule_time: When to post (datetime object)
            media_urls: List of public image URLs (optional)

        Returns:
            Ayrshare API response with post ID and status

        Raises:
            httpx.HTTPError: If API request fails
        """
        logger.info(f"📅 Scheduling post for {schedule_time.isoformat()} on {platforms}...")

        payload = {
            "post": post_text,
            "platforms": platforms,
            "scheduleDate": schedule_time.isoformat() + "Z"  # ISO-8601 with UTC
        }

        if media_urls:
            payload["mediaUrls"] = media_urls

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/post",
                headers=self.headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()

        logger.info(f"  ✅ Scheduled successfully: {data.get('id', 'N/A')}")
        return data

    async def post_recurring(
        self,
        post_text: str,
        platforms: List[str],
        repeat: int,
        days_interval: int,
        start_time: datetime,
        media_urls: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create recurring post using Ayrshare Auto Repost feature.

        Args:
            post_text: Text content for the post
            platforms: List of platform names
            repeat: Number of times to repeat (1-10)
            days_interval: Interval between posts in days (2+)
            start_time: When to start posting
            media_urls: List of public image URLs (optional)

        Returns:
            Ayrshare API response with post ID and status

        Raises:
            httpx.HTTPError: If API request fails
            ValueError: If repeat or days_interval is invalid
        """
        logger.info(f"🔁 Creating recurring post: {repeat} times every {days_interval} days on {platforms}...")

        # Validate Ayrshare limits
        if repeat < 1 or repeat > 10:
            raise ValueError("Repeat must be between 1 and 10")
        if days_interval < 2:
            raise ValueError("Days interval must be 2 or more")

        payload = {
            "post": post_text,
            "platforms": platforms,
            "scheduleDate": start_time.isoformat() + "Z",
            "autoRepost": {
                "repeat": repeat,
                "days": days_interval
            }
        }

        if media_urls:
            payload["mediaUrls"] = media_urls

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/post",
                headers=self.headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            data = response.json()

        logger.info(f"  ✅ Recurring post created: {data.get('id', 'N/A')}")
        return data

    async def delete_post(self, ayrshare_post_id: str) -> Dict[str, Any]:
        """
        Delete/cancel a scheduled or recurring post.

        Args:
            ayrshare_post_id: Ayrshare post ID to delete

        Returns:
            Ayrshare API response

        Raises:
            httpx.HTTPError: If API request fails
        """
        logger.info(f"🗑️ Deleting post {ayrshare_post_id}...")

        payload = {"id": ayrshare_post_id}

        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/delete",
                headers=self.headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        logger.info(f"  ✅ Post deleted successfully")
        return data

    async def get_post_status(self, ayrshare_post_id: str) -> Dict[str, Any]:
        """
        Get status of a specific post.

        Args:
            ayrshare_post_id: Ayrshare post ID

        Returns:
            Post status information

        Raises:
            httpx.HTTPError: If API request fails
        """
        logger.info(f"📊 Getting status for post {ayrshare_post_id}...")

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/post/{ayrshare_post_id}",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()

        logger.info(f"  ✓ Status retrieved: {data.get('status', 'unknown')}")
        return data
