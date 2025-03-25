from typing import List, Optional, Dict, Any, Tuple
from sqlmodel import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate
import logging

logger = logging.getLogger(__name__)


class LeadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_lead(self, lead: LeadCreate) -> Lead:
        """Create a new lead in the database"""
        # Convert the LeadCreate to a dictionary and create Lead model
        lead_dict = lead.model_dump()
        db_lead = Lead(**lead_dict)

        self.session.add(db_lead)
        await self.session.commit()
        await self.session.refresh(db_lead)
        return db_lead

    async def get_lead(self, lead_id: int) -> Optional[Lead]:
        """Get a lead by ID"""
        statement = select(Lead).where(Lead.id == lead_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_leads(self) -> List[Lead]:
        """Get all leads"""
        statement = select(Lead)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_leads_with_filters(
        self, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = {}
    ) -> Tuple[List[Lead], int]:
        """
        Get leads with pagination and filtering

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of field name to filter value

        Returns:
            Tuple of (leads list, total count)
        """
        # This check is no longer needed since we use an empty dict as default
        # but we can keep it for backward compatibility
        if filters is None:
            filters = {}

        # Start with base query
        query = select(Lead)
        count_query = select(func.count())

        # Apply filters if provided
        for field, value in filters.items():
            if hasattr(Lead, field):
                if isinstance(value, str) and not field.endswith("_id"):
                    # Case insensitive partial match for string fields
                    condition = getattr(Lead, field).ilike(f"%{value}%")
                else:
                    # Exact match for non-string fields
                    condition = getattr(Lead, field) == value

                query = query.where(condition)
                count_query = count_query.where(condition)

        # Get total count for pagination info
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        results = await self.session.execute(query)
        leads = list(results.scalars().all())

        return leads, total

    async def update_lead(
        self, lead_id: int, lead_update: LeadUpdate
    ) -> Optional[Lead]:
        """Update a lead with new data"""
        db_lead = await self.get_lead(lead_id)
        if db_lead:
            # Update lead fields
            lead_data = lead_update.model_dump(
                exclude_unset=True
            )  # Change from .dict() to .model_dump()
            for field, value in lead_data.items():
                setattr(db_lead, field, value)

            await self.session.commit()
            await self.session.refresh(db_lead)
            return db_lead
        return None

    async def delete_lead(self, lead_id: int) -> bool:
        """Delete a lead by ID"""
        db_lead = await self.get_lead(lead_id)
        if db_lead:
            await self.session.delete(db_lead)
            await self.session.commit()
            return True
        return False
