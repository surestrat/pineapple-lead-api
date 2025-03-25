from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from typing import AsyncGenerator
from app.core.config import settings
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Base(SQLModel):
    __abstract__ = True

    # Additional common fields can be added here if needed in the future.


# Get properly formatted async database URL
database_url = settings.get_async_database_url()

# Log the database URL (with password masked) for debugging
log_url = database_url
if "@" in log_url:
    # Mask password in logs
    parts = log_url.split("@")
    auth_parts = parts[0].split(":")
    if len(auth_parts) > 2:  # Has password
        masked_url = f"{auth_parts[0]}:****@{parts[1]}"
        log_url = masked_url

logger.info(f"Connecting to database with URL: {log_url}")

# Configure SQLite specially for async connections
if database_url.startswith("sqlite"):
    # Create the directory for SQLite db if it doesn't exist
    if "///" in database_url:
        db_path = database_url.split("///")[1]
        if db_path != ":memory:":
            directory = os.path.dirname(os.path.abspath(db_path))
            os.makedirs(directory, exist_ok=True)
            logger.info(f"SQLite database path: {db_path}")

    # SQLite-specific connect arguments
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

try:
    # Create async engine and sessionmaker
    async_engine = create_async_engine(
        database_url,
        connect_args=connect_args,
        echo=settings.DEBUG,  # Echo SQL in debug mode
    )
    async_session = async_sessionmaker(
        async_engine, expire_on_commit=False, autoflush=False
    )
    logger.info(f"Database engine and session created successfully")
except Exception as e:
    logger.error(f"Error creating database engine: {str(e)}")
    raise


# Update the get_async_session function
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async session for dependency injection."""
    try:
        async with async_session() as session:
            try:
                # Test the connection
                await session.execute(text("SELECT 1"))
                logger.info("Database connection test successful")
            except Exception as e:
                logger.error(f"Database connection test failed: {str(e)}")
                raise
            yield session
    except Exception as e:
        logger.error(f"Error creating database session: {str(e)}")
        raise
    finally:
        logger.debug("Closing database session")
