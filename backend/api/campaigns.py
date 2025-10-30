"""
Campaigns API router.

Handles all campaign-related endpoints.
"""
import json
import uuid
from typing import List
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from database import get_db
from models.orm import Campaign, Product
from models.pydantic import (
    CampaignCreate,
    CampaignWithProductsCreate,
    CampaignUpdate,
    CampaignRead,
    CampaignValidationResponse,
    ProductRead
)
from services.file_manager import process_image_path


router = APIRouter()


def parse_date_string(date_str):
    """
    Parse date string (YYYY-MM-DD) into Python date object.
    Returns None if date_str is None or empty.
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


@router.get("/campaigns", response_model=List[CampaignRead])
async def get_all_campaigns(db: Session = Depends(get_db)):
    """
    Retrieve all campaigns from the database.

    Returns:
        List of all campaigns with their details.
    """
    campaigns = db.query(Campaign).all()
    return campaigns


@router.get("/campaigns/{campaign_id}", response_model=CampaignRead)
async def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """
    Get a specific campaign by ID.

    Args:
        campaign_id: Campaign ID
        db: Database session

    Returns:
        Campaign details

    Raises:
        404: If campaign not found
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with id {campaign_id} not found"
        )
    return campaign


@router.post("/campaigns/validate", response_model=CampaignValidationResponse)
async def validate_campaign(data: dict = Body(...)):
    """
    Validate campaign data from JSON upload.
    Returns partial data and missing required fields.
    Handles optional products array in the campaign data.

    Args:
        data: Campaign data dictionary (may include 'products' array)

    Returns:
        Validation response with data and missing fields
    """
    required_fields = ["name", "campaign_message", "target_region", "target_audience"]
    missing_fields = [field for field in required_fields if not data.get(field)]

    # Extract products array if present (it's optional)
    products = data.pop("products", None)

    # Add products back to data for frontend to use
    if products:
        data["products"] = products

    return {
        "data": data,
        "missing_fields": missing_fields,
        "is_complete": len(missing_fields) == 0
    }


@router.post("/campaigns", response_model=CampaignRead, status_code=status.HTTP_201_CREATED)
async def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    """
    Create a new campaign.

    Args:
        campaign: Campaign data
        db: Database session

    Returns:
        Created campaign
    """
    # Process brand images - download URLs if needed
    brand_images_list = json.loads(campaign.brand_images)
    processed_images = []

    for image_path in brand_images_list:
        if image_path:
            processed_path = await process_image_path(image_path)
            processed_images.append(processed_path)

    # Create new campaign
    db_campaign = Campaign(
        id=str(uuid.uuid4()),
        name=campaign.name,
        campaign_message=campaign.campaign_message,
        call_to_action=campaign.call_to_action,
        target_region=campaign.target_region,
        target_audience=campaign.target_audience,
        brand_images=json.dumps(processed_images),
        start_date=campaign.start_date,
        duration=campaign.duration
    )

    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)

    return db_campaign


@router.post("/campaigns/with-products", status_code=status.HTTP_201_CREATED)
async def create_campaign_with_products(
    campaign_data: CampaignWithProductsCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new campaign with products from a single JSON upload.

    Args:
        campaign_data: Campaign data with nested products array
        db: Database session

    Returns:
        Created campaign with products included
    """
    # Process brand images - download URLs if needed
    brand_images_list = json.loads(campaign_data.brand_images)
    processed_images = []

    for image_path in brand_images_list:
        if image_path:
            processed_path = await process_image_path(image_path)
            processed_images.append(processed_path)

    # Create new campaign
    campaign_id = str(uuid.uuid4())
    db_campaign = Campaign(
        id=campaign_id,
        name=campaign_data.name,
        campaign_message=campaign_data.campaign_message,
        call_to_action=campaign_data.call_to_action,
        target_region=campaign_data.target_region,
        target_audience=campaign_data.target_audience,
        brand_images=json.dumps(processed_images),
        start_date=campaign_data.start_date,
        duration=campaign_data.duration
    )

    db.add(db_campaign)
    db.flush()  # Flush to get the campaign ID before creating products

    # Create products if provided
    created_products = []
    for product_data in campaign_data.products:
        # Process product image
        if product_data.image_path:
            processed_image = await process_image_path(product_data.image_path)
        else:
            processed_image = None

        db_product = Product(
            id=str(uuid.uuid4()),
            campaign_id=campaign_id,
            name=product_data.name,
            description=product_data.description,
            image_path=processed_image
        )
        db.add(db_product)
        created_products.append(db_product)

    db.commit()
    db.refresh(db_campaign)

    # Return campaign with products
    return {
        "campaign": CampaignRead.model_validate(db_campaign),
        "products": [ProductRead.model_validate(p) for p in created_products]
    }


@router.put("/campaigns/{campaign_id}", response_model=CampaignRead)
async def update_campaign(
    campaign_id: str,
    campaign_update: CampaignUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing campaign.

    Args:
        campaign_id: Campaign ID
        campaign_update: Fields to update
        db: Database session

    Returns:
        Updated campaign

    Raises:
        404: If campaign not found
    """
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not db_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with id {campaign_id} not found"
        )

    # Update only provided fields
    update_data = campaign_update.model_dump(exclude_unset=True)

    # Process brand images if provided
    if "brand_images" in update_data and update_data["brand_images"]:
        brand_images_list = json.loads(update_data["brand_images"])
        processed_images = []

        for image_path in brand_images_list:
            if image_path:
                processed_path = await process_image_path(image_path)
                processed_images.append(processed_path)

        update_data["brand_images"] = json.dumps(processed_images)

    for field, value in update_data.items():
        setattr(db_campaign, field, value)

    db.commit()
    db.refresh(db_campaign)

    return db_campaign


@router.delete("/campaigns/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """
    Delete a campaign and all its products.

    Args:
        campaign_id: Campaign ID
        db: Database session

    Raises:
        404: If campaign not found
    """
    db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not db_campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with id {campaign_id} not found"
        )

    db.delete(db_campaign)
    db.commit()

    return None
