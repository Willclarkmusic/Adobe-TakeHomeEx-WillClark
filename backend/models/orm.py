"""
SQLAlchemy ORM models for the Creative Automation Hub.
"""
from sqlalchemy import Column, String, Text, ForeignKey, Date, Integer, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Campaign(Base):
    """
    Campaign model representing a marketing campaign.

    Stores campaign metadata including target audience, region, and brand images.
    """
    __tablename__ = "campaigns"

    id = Column(String, primary_key=True, index=True)
    name = Column(Text, nullable=False)  # Campaign name for display
    campaign_message = Column(Text, nullable=False)
    call_to_action = Column(Text, nullable=True)  # CTA for posts
    target_region = Column(Text, nullable=False)
    target_audience = Column(Text, nullable=False)
    brand_images = Column(Text, nullable=False)  # JSON string of image paths
    start_date = Column(Date, nullable=True)  # Campaign start date
    duration = Column(Integer, nullable=True)  # Campaign duration in days

    # Relationships
    products = relationship("Product", back_populates="campaign", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="campaign", cascade="all, delete-orphan")


class Product(Base):
    """
    Product model representing a product within a campaign.

    Links to a campaign via foreign key and stores product details and image.
    """
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False, index=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    image_path = Column(Text, nullable=True)  # Relative path to file in /files/media/

    # Relationships
    campaign = relationship("Campaign", back_populates="products")
    posts = relationship("Post", back_populates="product", cascade="all, delete-orphan")


class Post(Base):
    """
    Post model representing an AI-generated social media post.

    Links to both a campaign and a product. Stores generated text content
    (headline, body, caption) and paths to generated images for multiple aspect ratios.
    """
    __tablename__ = "posts"

    id = Column(String, primary_key=True, index=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False, index=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False, index=True)
    headline = Column(Text, nullable=False)
    body_text = Column(Text, nullable=False)
    caption = Column(Text, nullable=False)
    text_color = Column(String, nullable=True)  # Hex color code for headline background
    image_1_1 = Column(Text, nullable=True)  # Path to 1:1 aspect ratio image
    image_16_9 = Column(Text, nullable=True)  # Path to 16:9 aspect ratio image
    image_9_16 = Column(Text, nullable=True)  # Path to 9:16 aspect ratio image
    generation_prompt = Column(Text, nullable=True)  # User's input prompt
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="posts")
    product = relationship("Product", back_populates="posts")
