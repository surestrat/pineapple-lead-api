from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db.base import get_async_session
import platform
import time

router = APIRouter()


class HealthCheck(BaseModel):
    status: str
    environment: str
    version: str
    timestamp: float
    database_connection: bool
    system_info: dict


@router.get("/health", response_model=HealthCheck)
async def health_check(session: AsyncSession = Depends(get_async_session)):
    """
    Health check endpoint for monitoring the API.

    Returns status information about the API and its dependencies.
    """
    from app.core.config import settings

    # Check database connection
    db_connection = True
    try:
        from sqlalchemy import text

        result = await session.execute(text("SELECT 1"))
        result.fetchone()
    except Exception:
        db_connection = False

    return {
        "status": "healthy",
        "environment": "production" if not settings.DEBUG else "development",
        "version": settings.VERSION,
        "timestamp": time.time(),
        "database_connection": db_connection,
        "system_info": {
            "python_version": platform.python_version(),
            "system": platform.system(),
            "processor": platform.processor(),
        },
    }


@router.get("/ping")
async def ping():
    """Simple ping endpoint for basic health checking"""
    return {"ping": "pong"}
