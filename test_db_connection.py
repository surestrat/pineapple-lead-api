"""
Simple script to test the database connection.
This helps isolate database connection issues.
"""

import asyncio
import logging
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_connection():
    # Get database URL with async driver
    db_url = settings.get_async_database_url()
    logger.info(f"Testing connection to: {db_url}")

    # Create engine with appropriate connect args
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    try:
        # Create engine
        engine = create_async_engine(db_url, connect_args=connect_args, echo=True)
        logger.info("Engine created successfully")

        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info(
                f"Database connection test successful! Result: {result.scalar()}"
            )
    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(test_connection())
