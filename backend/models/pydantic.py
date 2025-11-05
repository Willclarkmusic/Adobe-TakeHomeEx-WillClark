"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class CampaignCreate(BaseModel):
    """
    Schema for creating a new campaign.
    """
    name: str
    campaign_message: str
    call_to_action: Optional[str] = None
    target_region: str
    target_audience: str
    brand_images: Optional[str] = "[]"  # JSON string, defaults to empty array
    start_date: Optional[date] = None
    duration: Optional[int] = None  # Duration in days


class CampaignWithProductsCreate(BaseModel):
    """
    Schema for creating a campaign with nested products in one request.
    """
    name: str
    campaign_message: str
    call_to_action: Optional[str] = None
    target_region: str
    target_audience: str
    brand_images: Optional[str] = "[]"  # JSON string, defaults to empty array
    start_date: Optional[date] = None
    duration: Optional[int] = None  # Duration in days
    products: Optional[List["ProductCreateNested"]] = []


class CampaignUpdate(BaseModel):
    """
    Schema for updating an existing campaign.
    """
    name: Optional[str] = None
    campaign_message: Optional[str] = None
    call_to_action: Optional[str] = None
    target_region: Optional[str] = None
    target_audience: Optional[str] = None
    brand_images: Optional[str] = None
    start_date: Optional[date] = None
    duration: Optional[int] = None


class CampaignRead(BaseModel):
    """
    Schema for reading/returning campaign data via API.
    """
    id: str
    name: str
    campaign_message: str
    call_to_action: Optional[str] = None
    target_region: str
    target_audience: str
    brand_images: str  # JSON string
    start_date: Optional[date] = None
    duration: Optional[int] = None

    class Config:
        from_attributes = True  # Allows ORM model conversion (previously orm_mode)


class CampaignValidationResponse(BaseModel):
    """
    Schema for validation response with partial data and missing fields.
    """
    data: dict
    missing_fields: List[str]
    is_complete: bool


class ProductCreateNested(BaseModel):
    """
    Schema for creating a product nested within a campaign (no campaign_id needed).
    """
    name: str
    description: Optional[str] = None
    image_path: Optional[str] = None


class ProductCreate(BaseModel):
    """
    Schema for creating a new product.
    """
    campaign_id: str
    name: str
    description: Optional[str] = None
    image_path: Optional[str] = None


class ProductUpdate(BaseModel):
    """
    Schema for updating an existing product.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    image_path: Optional[str] = None


class ProductValidationResponse(BaseModel):
    """
    Schema for product validation response with partial data and missing fields.
    """
    data: dict
    missing_fields: List[str]
    is_complete: bool


class ProductBatchValidationResponse(BaseModel):
    """
    Schema for batch product validation response.
    Returns validation results for multiple products.
    """
    valid_products: List[dict]  # Products that passed validation
    invalid_products: List[dict]  # Products with errors (includes error messages)
    is_complete: bool  # True if all products are valid


class ProductBatchCreate(BaseModel):
    """
    Schema for creating multiple products in a single request.
    """
    products: List[ProductCreate]


class ProductRead(BaseModel):
    """
    Schema for reading/returning product data via API.
    """
    id: str
    campaign_id: str
    name: str
    description: Optional[str] = None
    image_path: Optional[str] = None

    class Config:
        from_attributes = True


class PostCreate(BaseModel):
    """
    Schema for creating a new post manually.
    """
    campaign_id: str
    product_id: Optional[str] = None  # Now optional
    mood_id: Optional[str] = None  # New field
    source_images: Optional[List[str]] = None  # New field: JSON array of image paths
    headline: str
    body_text: str
    caption: str
    text_color: Optional[str] = None
    image_1_1: Optional[str] = None
    image_16_9: Optional[str] = None
    image_9_16: Optional[str] = None
    generation_prompt: Optional[str] = None


class PostUpdate(BaseModel):
    """
    Schema for updating an existing post.
    """
    headline: Optional[str] = None
    body_text: Optional[str] = None
    caption: Optional[str] = None
    text_color: Optional[str] = None
    image_1_1: Optional[str] = None
    image_16_9: Optional[str] = None
    image_9_16: Optional[str] = None
    generation_prompt: Optional[str] = None


class PostRead(BaseModel):
    """
    Schema for reading/returning post data via API.
    """
    id: str
    campaign_id: str
    product_id: Optional[str] = None  # Now optional
    mood_id: Optional[str] = None  # New field
    source_images: Optional[str] = None  # New field: JSON string (stored as TEXT in DB)
    headline: str
    body_text: str
    caption: str
    text_color: Optional[str] = None
    image_1_1: Optional[str] = None
    image_16_9: Optional[str] = None
    image_9_16: Optional[str] = None
    generation_prompt: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PostGenerateRequest(BaseModel):
    """
    Schema for AI post generation request.
    User provides source images (from products or mood board), prompt, and desired aspect ratios.
    """
    campaign_id: str
    source_images: List[str]  # Array of image paths (products or mood board images)
    prompt: str
    aspect_ratios: List[str] = ["1:1"]  # Default to 1:1, can include "16:9", "9:16"


class PostRegenerateRequest(BaseModel):
    """
    Schema for regenerating post images.
    Replaces existing images with newly generated ones.
    """
    product_id: str
    prompt: str
    aspect_ratios: List[str] = ["1:1"]  # Aspect ratios to regenerate


class MoodMediaCreate(BaseModel):
    """
    Schema for creating mood media manually.
    """
    campaign_id: str
    file_path: str
    media_type: str  # "image" or "video"
    is_generated: bool = False
    prompt: Optional[str] = None
    source_images: Optional[str] = None  # JSON array
    aspect_ratio: Optional[str] = None
    generation_metadata: Optional[str] = None  # JSON object


class MoodMediaRead(BaseModel):
    """
    Schema for reading/returning mood media data via API.
    """
    id: str
    campaign_id: str
    file_path: str
    gcs_uri: Optional[str] = None
    media_type: str
    is_generated: bool
    prompt: Optional[str] = None
    source_images: Optional[str] = None
    aspect_ratio: Optional[str] = None
    generation_metadata: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MoodImageGenerateRequest(BaseModel):
    """
    Schema for mood board image generation request.
    Generates 1-3 separate images (one per ratio).
    """
    campaign_id: str
    prompt: str
    source_images: List[str] = []  # Paths to source images
    ratios: List[str] = ["1:1"]  # Up to 3 ratios: "1:1", "3:4", "4:3", "9:16", "16:9"


class MoodVideoGenerateRequest(BaseModel):
    """
    Schema for mood board video generation request (Veo).
    Generates a single video.
    """
    campaign_id: str
    prompt: str
    source_images: List[str] = []  # Max 3 source images
    ratio: str = "16:9"  # "16:9" or "9:16"
    duration: int = 6  # 4, 6, or 8 seconds


class MoodAvailableImagesResponse(BaseModel):
    """
    Schema for returning available images for mood generation.
    Includes products and existing mood images.
    """
    products: List[ProductRead]
    mood_images: List[MoodMediaRead]


class AyrshareProfile(BaseModel):
    """
    Schema for Ayrshare connected social media account/profile.
    """
    profile_key: str  # Ayrshare profile key (unique identifier)
    platform: str  # Platform name (e.g., "instagram", "facebook", "twitter")
    username: Optional[str] = None  # Account username/handle
    display_name: Optional[str] = None  # Account display name
    is_active: bool = True  # Whether profile is active


class AyrshareProfilesResponse(BaseModel):
    """
    Schema for Ayrshare profiles API response.
    """
    profiles: List[AyrshareProfile]


class RecurringConfig(BaseModel):
    """
    Schema for recurring post configuration.
    """
    repeat: int  # Number of times to repeat (1-10 for Ayrshare)
    days: int  # Interval between posts in days (2+ for Ayrshare)
    order: str = "sequential"  # "sequential" or "random"
    post_ids: Optional[List[str]] = []  # List of post IDs for rotation (sequential mode)


class SchedulePostRequest(BaseModel):
    """
    Schema for scheduling a social media post via Ayrshare.
    """
    post_id: str  # ID of the post to schedule
    campaign_id: str  # Campaign ID for filtering
    schedule_type: str  # "immediate", "scheduled", or "recurring"
    platforms: List[str]  # Platform names (e.g., ["instagram", "facebook"])
    schedule_time: Optional[datetime] = None  # Required for "scheduled", null for "immediate"
    recurring_config: Optional[RecurringConfig] = None  # Required for "recurring"


class ScheduledPostRead(BaseModel):
    """
    Schema for reading/returning scheduled post data via API.
    Includes post details for display.
    """
    id: str
    post_id: str
    campaign_id: str
    schedule_type: str
    platforms: str  # JSON array
    schedule_time: Optional[datetime] = None
    recurring_config: Optional[str] = None  # JSON object
    ayrshare_post_id: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    # Nested post data for display
    post: Optional[PostRead] = None

    class Config:
        from_attributes = True


class ScheduledPostsResponse(BaseModel):
    """
    Schema for returning list of scheduled posts.
    """
    scheduled_posts: List[ScheduledPostRead]
