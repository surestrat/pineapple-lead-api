from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from app.db.base import get_async_session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session = await anext(get_async_session())
    try:
        yield session
    finally:
        await session.close()
