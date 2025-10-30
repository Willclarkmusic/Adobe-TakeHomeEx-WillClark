"""
Products API router.

Handles all product-related CRUD endpoints.
"""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session
from database import get_db
from models.orm import Product, Campaign
from models.pydantic import ProductCreate, ProductUpdate, ProductRead, ProductValidationResponse
from services.file_manager import process_image_path


router = APIRouter()


@router.get("/products", response_model=List[ProductRead])
async def get_products(campaign_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """
    Get all products, optionally filtered by campaign_id.

    Args:
        campaign_id: Optional campaign ID to filter products
        db: Database session

    Returns:
        List of products (filtered by campaign if provided)
    """
    query = db.query(Product)
    if campaign_id:
        query = query.filter(Product.campaign_id == campaign_id)

    products = query.all()
    return products


@router.post("/products/validate", response_model=ProductValidationResponse)
async def validate_product(data: dict = Body(...)):
    """
    Validate product data from JSON upload.
    Returns partial data and missing required fields.

    Args:
        data: Product data dictionary

    Returns:
        Validation response with data and missing fields
    """
    required_fields = ["name", "campaign_id"]
    missing_fields = [field for field in required_fields if not data.get(field)]

    return {
        "data": data,
        "missing_fields": missing_fields,
        "is_complete": len(missing_fields) == 0
    }


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product.

    Args:
        product: Product data from request body
        db: Database session

    Returns:
        Created product

    Raises:
        404: If campaign not found
    """
    # Verify campaign exists
    campaign = db.query(Campaign).filter(Campaign.id == product.campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with id {product.campaign_id} not found"
        )

    # Process image path - download if URL
    image_path = product.image_path
    if image_path:
        image_path = await process_image_path(image_path)

    # Create new product
    db_product = Product(
        id=str(uuid.uuid4()),
        campaign_id=product.campaign_id,
        name=product.name,
        description=product.description,
        image_path=image_path
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


@router.get("/campaigns/{campaign_id}/products", response_model=List[ProductRead])
async def get_products_by_campaign(campaign_id: str, db: Session = Depends(get_db)):
    """
    Get all products for a specific campaign.

    Args:
        campaign_id: Campaign ID
        db: Database session

    Returns:
        List of products for the campaign

    Raises:
        404: If campaign not found
    """
    # Verify campaign exists
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign with id {campaign_id} not found"
        )

    products = db.query(Product).filter(Product.campaign_id == campaign_id).all()
    return products


@router.get("/products/{product_id}", response_model=ProductRead)
async def get_product(product_id: str, db: Session = Depends(get_db)):
    """
    Get a specific product by ID.

    Args:
        product_id: Product ID
        db: Database session

    Returns:
        Product details

    Raises:
        404: If product not found
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )

    return product


@router.put("/products/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing product.

    Args:
        product_id: Product ID
        product_update: Fields to update
        db: Database session

    Returns:
        Updated product

    Raises:
        404: If product not found
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )

    # Update only provided fields
    update_data = product_update.model_dump(exclude_unset=True)

    # Process image path if provided - download if URL
    if "image_path" in update_data and update_data["image_path"]:
        update_data["image_path"] = await process_image_path(update_data["image_path"])

    for field, value in update_data.items():
        setattr(db_product, field, value)

    db.commit()
    db.refresh(db_product)

    return db_product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, db: Session = Depends(get_db)):
    """
    Delete a product.

    Args:
        product_id: Product ID
        db: Database session

    Raises:
        404: If product not found
    """
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )

    db.delete(db_product)
    db.commit()

    return None
