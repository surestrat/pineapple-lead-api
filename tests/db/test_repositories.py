from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.repositories.lead_repository import LeadRepository
from app.db.repositories.quote_repository import QuoteRepository
from app.models.lead import Lead
from app.models.quote import Quote
from app.schemas.lead import LeadCreate
from app.schemas.quote import QuoteCreate
import pytest


@pytest.fixture
async def async_session() -> AsyncSession:
    # Setup code for creating an async session
    from sqlalchemy.ext.asyncio import (
        create_async_engine,
        AsyncSession,
        async_sessionmaker,
    )
    from app.db.base import Base

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return async_session()


@pytest.fixture
async def lead_repository(async_session: AsyncSession) -> LeadRepository:
    return LeadRepository(async_session)


@pytest.fixture
async def quote_repository(async_session: AsyncSession) -> QuoteRepository:
    return QuoteRepository(async_session)


@pytest.mark.asyncio
async def test_create_lead(lead_repository: LeadRepository):
    lead_data = LeadCreate(
        name="Test Lead",
        email="test@example.com",
        phone="1234567890",
        company="Test Company",
        status="NEW",
    )
    created_lead = await lead_repository.create_lead(lead_data)
    assert created_lead.id is not None
    assert created_lead.name == lead_data.name


@pytest.mark.asyncio
async def test_get_lead(lead_repository: LeadRepository):
    lead_data = LeadCreate(
        name="Test Lead",
        email="test@example.com",
        phone="1234567890",
        company="Test Company",
        status="NEW",
    )
    created_lead = await lead_repository.create_lead(lead_data)
    assert created_lead.id is not None  # Ensure ID exists
    fetched_lead = await lead_repository.get_lead(created_lead.id)
    assert fetched_lead is not None  # Ensure lead was found
    assert fetched_lead.id == created_lead.id
    assert fetched_lead.name == created_lead.name


@pytest.mark.asyncio
async def test_create_quote(quote_repository: QuoteRepository):
    quote_data = QuoteCreate(
        description="Test Quote", amount=100.0, currency="USD", lead_id=1
    )
    created_quote = await quote_repository.create_quote(quote_data)
    assert created_quote.id is not None
    assert created_quote.quote_description == quote_data.description
    assert created_quote.quote_amount == quote_data.amount


@pytest.mark.asyncio
async def test_get_quote(quote_repository: QuoteRepository):
    quote_data = QuoteCreate(
        description="Test Quote", amount=100.0, currency="USD", lead_id=1
    )
    created_quote = await quote_repository.create_quote(quote_data)
    assert created_quote.id is not None
    fetched_quote = await quote_repository.get_quote(created_quote.id)
    assert fetched_quote is not None
    assert fetched_quote.id == created_quote.id
    assert fetched_quote.quote_amount == created_quote.quote_amount
