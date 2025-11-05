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
from models.pydantic import (
    ProductCreate, ProductUpdate, ProductRead, ProductValidationResponse,
    ProductBatchCreate, ProductBatchValidationResponse, ProductRegenerateImageRequest
)
from services.file_manager import process_image_path, save_generated_product_image
from services.gemini_service import GeminiService


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


@router.post("/products/batch/validate", response_model=ProductBatchValidationResponse)
async def validate_products_batch(data: List[dict] = Body(...)):
    """
    Validate multiple products from batch JSON upload.
    Returns validation results for all products.

    Args:
        data: List of product data dictionaries

    Returns:
        Batch validation response with valid and invalid products
    """
    required_fields = ["name", "campaign_id"]
    valid_products = []
    invalid_products = []

    for index, product_data in enumerate(data):
        missing_fields = [field for field in required_fields if not product_data.get(field)]

        if len(missing_fields) == 0:
            valid_products.append(product_data)
        else:
            invalid_products.append({
                "index": index,
                "data": product_data,
                "errors": f"Missing fields: {', '.join(missing_fields)}"
            })

    return {
        "valid_products": valid_products,
        "invalid_products": invalid_products,
        "is_complete": len(invalid_products) == 0
    }


@router.post("/products/batch", response_model=List[ProductRead], status_code=status.HTTP_201_CREATED)
async def create_products_batch(batch_data: ProductBatchCreate, db: Session = Depends(get_db)):
    """
    Create multiple products in a single transaction.
    All products must be valid or the entire batch fails (transaction rollback).

    Args:
        batch_data: Batch create request with list of products
        db: Database session

    Returns:
        List of created products

    Raises:
        404: If any campaign not found
        500: If any product creation fails
    """
    created_products = []

    try:
        for product in batch_data.products:
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
            created_products.append(db_product)

        # Commit all products in single transaction
        db.commit()

        # Refresh all products to get generated fields
        for product in created_products:
            db.refresh(product)

        return created_products

    except HTTPException:
        # Re-raise HTTP exceptions
        db.rollback()
        raise
    except Exception as e:
        # Rollback on any error
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch product creation failed: {str(e)}"
        )


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


@router.post("/products/{product_id}/regenerate-image", response_model=ProductRead)
async def regenerate_product_image(
    product_id: str,
    request: ProductRegenerateImageRequest = Body(default=ProductRegenerateImageRequest()),
    db: Session = Depends(get_db)
):
    """
    Regenerate a product image using AI when the current image is missing or unreadable.

    Uses Google Gemini to generate a professional product photo from the product's
    name and description.

    Args:
        product_id: Product ID
        request: Optional user prompt for style guidance
        db: Database session

    Returns:
        Updated product with new image_path

    Raises:
        404: If product not found
        500: If image generation or save fails
    """
    # Fetch the product
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )

    try:
        print(f"🎨 Regenerating image for product: {db_product.name}")

        # Initialize Gemini service
        gemini_service = GeminiService()

        # Generate image from text using product information
        generated_image = await gemini_service.generate_product_image_from_text(
            product_name=db_product.name,
            product_description=db_product.description,
            user_prompt=request.user_prompt
        )

        print(f"✅ Image generated successfully")

        # Save the generated image
        new_image_path = await save_generated_product_image(
            image=generated_image,
            product_name=db_product.name
        )

        print(f"✅ Image saved to: {new_image_path}")

        # Update product with new image path
        db_product.image_path = new_image_path
        db.commit()
        db.refresh(db_product)

        print(f"✅ Product updated with new image path")

        return db_product

    except Exception as e:
        db.rollback()
        print(f"❌ Image regeneration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate product image: {str(e)}"
        )
