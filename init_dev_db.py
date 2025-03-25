"""
Initialize development database with SQLite
Run this script to create tables and populate with initial data
"""

import asyncio
import os
import logging
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment or use default SQLite
database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")
logger.info(f"Using database URL: {database_url}")

# Make sure we're using the async driver for SQLite
if database_url.startswith("sqlite") and not database_url.startswith(
    "sqlite+aiosqlite"
):
    database_url = database_url.replace("sqlite", "sqlite+aiosqlite", 1)
    logger.info(f"Updated to async SQLite URL: {database_url}")


async def init_db():
    try:
        # Import all models to ensure they're registered with SQLModel
        from app.models.lead import Lead
        from app.models.quote import Quote

        logger.info("Models imported successfully")

        # Create async engine
        connect_args = (
            {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        )
        engine = create_async_engine(
            database_url, connect_args=connect_args, echo=True  # Show SQL commands
        )
        logger.info("Engine created successfully")

        # Create all tables
        async with engine.begin() as conn:
            logger.info("Creating database tables...")
            await conn.run_sync(SQLModel.metadata.create_all)

        logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(init_db())
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
