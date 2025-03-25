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


from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)):
    # Logic to retrieve the current user based on the token
    pass


def get_lead_repository(session: AsyncSession = Depends(get_db_session)):
    from app.db.repositories.lead_repository import LeadRepository

    return LeadRepository(session)


def get_quote_repository(session: AsyncSession = Depends(get_db_session)):
    from app.db.repositories.quote_repository import QuoteRepository

    return QuoteRepository(session)
