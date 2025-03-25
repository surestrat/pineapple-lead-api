from sqlalchemy.orm import Session
from app.db.repositories.quote_repository import QuoteRepository
from app.schemas.quote import (
    QuoteCreate,
    QuoteRead,
    QuoteUpdate,
    PineappleQuickQuoteRequest,
    PineappleQuickQuoteResponse,
    Vehicle,
)
import httpx
import logging
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class QuoteService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.quote_repository = QuoteRepository(db)
        self.pineapple_api_url = (
            "http://gw-test.pineapple.co.za/api/v1/quote/quick-quote"
        )
        self.auth_token = settings.PINEAPPLE_API_TOKEN

    async def create_pineapple_quote(
        self, quote_request: PineappleQuickQuoteRequest
    ) -> PineappleQuickQuoteResponse:
        """Request a quick quote from Pineapple's API"""
        logger.info(
            f"Requesting quote from Pineapple for reference: {quote_request.externalReferenceId}"
        )

        payload = quote_request.model_dump(exclude_unset=True)

        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.pineapple_api_url, json=payload, headers=headers, timeout=30.0
                )

                response.raise_for_status()

                result = response.json()

                if result.get("success") and len(result.get("data", [])) > 0:
                    premium = result["data"][0].get("premium", 0)
                    quote_id = result.get("id", "")

                    quote_create = QuoteCreate(
                        lead_id=1,
                        amount=premium,
                        description=f"Pineapple vehicle quote for {quote_request.vehicles[0].make} {quote_request.vehicles[0].model}",
                        currency="ZAR",
                    )

                    await self.create_quote(quote_create)

                return PineappleQuickQuoteResponse(
                    success=result.get("success", False),
                    id=result.get("id", ""),
                    data=result.get("data", []),
                )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting quote from Pineapple: {str(e)}")
            raise ValueError(f"Failed to get quote from Pineapple: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting quote from Pineapple: {str(e)}")
            raise ValueError(f"Internal error getting quote: {str(e)}")

    async def create_quote(self, quote_data: QuoteCreate) -> QuoteRead:
        quote = await self.quote_repository.create_quote(quote_data)
        return QuoteRead.model_validate(quote)

    async def get_quote(self, quote_id: int) -> QuoteRead:
        quote = await self.quote_repository.get_quote(quote_id)
        if not quote:
            raise ValueError(f"Quote with ID {quote_id} not found")
        return QuoteRead.model_validate(quote)

    async def list_quotes(self) -> list[QuoteRead]:
        quotes = await self.quote_repository.get_quotes()
        return [QuoteRead.model_validate(quote) for quote in quotes]

    async def update_quote(self, quote_id: int, quote_data: QuoteUpdate) -> QuoteRead:
        updated_quote = await self.quote_repository.update_quote(quote_id, quote_data)
        if not updated_quote:
            raise ValueError(f"Quote with ID {quote_id} not found")
        return QuoteRead.model_validate(updated_quote)

    async def delete_quote(self, quote_id: int) -> None:
        await self.quote_repository.delete_quote(quote_id)
