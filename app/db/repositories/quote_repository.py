from typing import List, Optional, Dict, Any, Tuple
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select as async_select
from app.models.quote import Quote
from app.schemas.quote import QuoteCreate, QuoteUpdate, QuoteRead
import logging

logger = logging.getLogger(__name__)


class QuoteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_quote(self, quote: QuoteCreate) -> Quote:
        """Create a new quote in the database"""
        try:
            # Map schema fields to model fields
            db_quote = Quote(
                lead_id=quote.lead_id,
                quote_amount=quote.amount,
                quote_description=quote.description,
                created_at=None,  # This would be handled by database default
            )

            self.session.add(db_quote)
            await self.session.commit()
            await self.session.refresh(db_quote)
            return db_quote
        except Exception as e:
            logger.error(f"Error creating quote: {str(e)}")
            await self.session.rollback()
            raise

    async def get_quote(self, quote_id: int) -> Optional[Quote]:
        """Get a quote by ID"""
        statement = select(Quote).where(Quote.id == quote_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_quotes(self) -> List[Quote]:
        """Get all quotes"""
        statement = select(Quote)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_quotes_with_filters(
        self, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = {}
    ) -> Tuple[List[Quote], int]:
        """
        Get quotes with pagination and filtering

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of field name to filter value

        Returns:
            Tuple of (quotes list, total count)
        """
        if filters is None:
            filters = {}

        # Start with base query
        query = select(Quote)
        count_query = select(func.count()).select_from(Quote)

        # Apply filters if provided
        if "lead_id" in filters and filters["lead_id"] is not None:
            condition = Quote.lead_id == filters["lead_id"]
            query = query.where(condition)
            count_query = count_query.where(condition)

        if "min_amount" in filters and filters["min_amount"] is not None:
            condition = Quote.quote_amount >= filters["min_amount"]
            query = query.where(condition)
            count_query = count_query.where(condition)

        if "max_amount" in filters and filters["max_amount"] is not None:
            condition = Quote.quote_amount <= filters["max_amount"]
            query = query.where(condition)
            count_query = count_query.where(condition)

        # Get total count for pagination info
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        results = await self.session.execute(query)
        quotes = list(results.scalars().all())

        return quotes, total

    async def update_quote(self, quote_id: int, quote: QuoteUpdate) -> Optional[Quote]:
        """Update a quote with new data"""
        db_quote = await self.get_quote(quote_id)
        if db_quote:
            # Update fields that are provided
            update_data = quote.model_dump(
                exclude_unset=True
            )  # Change from .dict() to .model_dump()

            if "description" in update_data:
                db_quote.quote_description = update_data["description"]

            if "amount" in update_data:
                db_quote.quote_amount = update_data["amount"]

            await self.session.commit()
            await self.session.refresh(db_quote)
            return db_quote
        return None

    async def delete_quote(self, quote_id: int) -> bool:
        """Delete a quote by ID"""
        db_quote = await self.get_quote(quote_id)
        if db_quote:
            await self.session.delete(db_quote)
            await self.session.commit()
            return True
        return False
