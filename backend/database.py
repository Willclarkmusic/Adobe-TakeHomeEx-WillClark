"""
Database configuration and session management for SQLite.
"""
import json
import uuid
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# Create SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency function that yields a database session.
    Used in FastAPI endpoints to manage database connections.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_initial_data():
    """
    Populate the database with initial sample data if campaigns table is empty.
    This function is called on application startup.
    """
    from models.orm import Campaign

    db = SessionLocal()
    try:
        # Check if campaigns table is empty
        existing_campaigns = db.query(Campaign).count()

        if existing_campaigns == 0:
            # Create sample campaign
            sample_campaign = Campaign(
                id=str(uuid.uuid4()),
                name="Eco-Friendly Product Launch 2025",
                campaign_message="Launch our new eco-friendly product line with stunning visuals",
                call_to_action="Shop Now and Save the Planet!",
                target_region="North America",
                target_audience="Environmentally conscious millennials aged 25-40",
                brand_images=json.dumps([
                    "https://picsum.photos/seed/eco1/400/300",
                    "https://picsum.photos/seed/eco2/400/300"
                ]),
                start_date=None,
                duration=None
            )

            db.add(sample_campaign)
            db.commit()
            print("✅ Seeded initial campaign data")
        else:
            print(f"ℹ️  Database already contains {existing_campaigns} campaign(s)")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()
