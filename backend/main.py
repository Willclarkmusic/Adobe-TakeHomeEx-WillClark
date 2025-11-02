"""
FastAPI main application entry point.

Configures CORS, static file serving, database initialization, and API routing.
"""
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import Base, engine, seed_initial_data
from api.campaigns import router as campaigns_router
from api.products import router as products_router
from api.media import router as media_router
from api.posts import router as posts_router
from api.moods import router as moods_router

# Import ORM models to ensure they're registered with SQLAlchemy
from models.orm import Campaign, Product, Post, MoodMedia


# Create FastAPI application
app = FastAPI(
    title="Creative Automation Hub API",
    description="Backend API for the FDE Creative Automation Pipeline PoC",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers (register before static files to prioritize API routes)
app.include_router(campaigns_router, prefix="/api", tags=["Campaigns"])
app.include_router(products_router, prefix="/api", tags=["Products"])
app.include_router(posts_router, prefix="/api", tags=["Posts"])
app.include_router(media_router, prefix="/api", tags=["Media"])
app.include_router(moods_router, tags=["Moods"])

# Mount static files directory
# Get the absolute path to the files directory
BASE_DIR = Path(__file__).resolve().parent.parent
FILES_DIR = BASE_DIR / "files"
if FILES_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FILES_DIR)), name="static")
    print(f"✅ Static files mounted from: {FILES_DIR}")
else:
    print(f"⚠️  Warning: Static files directory not found at {FILES_DIR}")


@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    Creates database tables and seeds initial data if needed.
    """
    print("🚀 Starting Creative Automation Hub API...")

    # Create all database tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified")

    # Seed initial data
    seed_initial_data()


@app.get("/")
async def root():
    """
    Root endpoint - health check.
    """
    return {
        "message": "Creative Automation Hub API is running",
        "status": "healthy",
        "docs": "/docs"
    }
