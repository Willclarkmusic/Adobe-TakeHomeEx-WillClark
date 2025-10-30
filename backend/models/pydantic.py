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
    product_id: str
    headline: str
    body_text: str
    caption: str
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
    product_id: str
    headline: str
    body_text: str
    caption: str
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
    User provides product, prompt, and desired aspect ratios.
    """
    campaign_id: str
    product_id: str
    prompt: str
    aspect_ratios: List[str] = ["1:1"]  # Default to 1:1, can include "16:9", "9:16"
