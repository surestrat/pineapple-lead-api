from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession  # Change import
from app.db.repositories.lead_repository import LeadRepository
from app.schemas.lead import (
    LeadCreate,
    LeadUpdate,
    LeadTransferRequest,
    LeadTransferResponse,
    PineappleLeadTransferRequest,
    PineappleLeadTransferResponse,
)
from app.models.lead import Lead
from typing import Dict, Any, List, Tuple, Optional
import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class LeadTransferService:
    def __init__(self, db: AsyncSession):  # Change type annotation
        self.db = db  # Store the session
        self.lead_repository = LeadRepository(db)  # Pass session to repository
        self.pineapple_api_url = "http://gw-test.pineapple.co.za/users/motor_lead"
        # Token should be stored in settings and not hardcoded here
        self.auth_token = settings.PINEAPPLE_API_TOKEN

    async def transfer_lead(
        self, transfer_request: LeadTransferRequest
    ) -> LeadTransferResponse:
        """Transfer a lead to a new owner in the local system"""
        logger.info(
            f"Transferring lead {transfer_request.lead_id} to owner {transfer_request.new_owner_id}"
        )

        lead = await self.lead_repository.get_lead(transfer_request.lead_id)
        if not lead:
            logger.warning(f"Lead not found: {transfer_request.lead_id}")
            raise ValueError(f"Lead with ID {transfer_request.lead_id} not found")

        # In a real app, you would update owner_id field
        # For this example, we'll create a response
        return LeadTransferResponse(
            lead_id=transfer_request.lead_id, new_owner_id=transfer_request.new_owner_id
        )

    async def transfer_lead_to_pineapple(
        self, lead_data: PineappleLeadTransferRequest
    ) -> PineappleLeadTransferResponse:
        """Transfer a lead to the Pineapple system via their API"""
        logger.info(f"Transferring lead to Pineapple: {lead_data.email}")

        # Create the payload for Pineapple API
        payload = {
            "source": lead_data.source,
            "first_name": lead_data.first_name,
            "last_name": lead_data.last_name,
            "email": lead_data.email,
            "id_number": lead_data.id_number,
            "quote_id": lead_data.quote_id,
            "contact_number": lead_data.contact_number,
        }

        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.pineapple_api_url,
                    json=payload,
                    headers=headers,
                    timeout=30.0,  # Adjust timeout as needed
                )

                response.raise_for_status()  # Raise exception for non-200 responses

                result = response.json()

                # Store the lead in our local database
                lead_create = LeadCreate(
                    name=f"{lead_data.first_name} {lead_data.last_name}",
                    email=lead_data.email,
                    phone=lead_data.contact_number,
                    source=lead_data.source,
                    company="Pineapple",  # Set a default value since company is not in the request
                    # Make sure these fields match the schema definition in LeadCreate
                    # Set proper status enum value
                    status="new",  # Using a standard status value from LeadStatusEnum
                    # Add notes field with transfer information
                    notes=f"Transferred to Pineapple. Quote ID: {lead_data.quote_id or 'N/A'}",
                )

                await self.create_lead(lead_create)

                return PineappleLeadTransferResponse(
                    success=result.get("success", False),
                    uuid=result.get("data", {}).get("uuid", ""),
                    redirect_url=result.get("data", {}).get("redirect_url", ""),
                )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error transferring lead to Pineapple: {str(e)}")
            raise ValueError(f"Failed to transfer lead to Pineapple: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error transferring lead to Pineapple: {str(e)}")
            raise ValueError(f"Internal error transferring lead: {str(e)}")

    async def create_lead(self, lead_data: LeadCreate) -> Lead:
        """Create a new lead"""
        logger.info(f"Creating lead with email: {lead_data.email}")
        return await self.lead_repository.create_lead(lead_data)

    async def get_lead(self, lead_id: int) -> Optional[Lead]:
        """Get a lead by ID"""
        logger.info(f"Fetching lead with ID: {lead_id}")
        return await self.lead_repository.get_lead(lead_id)

    async def update_lead(self, lead_id: int, lead_data: LeadUpdate) -> Optional[Lead]:
        """Update a lead with new data"""
        logger.info(f"Updating lead with ID: {lead_id}")

        lead = await self.lead_repository.get_lead(lead_id)
        if not lead:
            logger.warning(f"Lead not found for update: {lead_id}")
            return None

        updated_lead = await self.lead_repository.update_lead(lead_id, lead_data)
        return updated_lead

    async def delete_lead(self, lead_id: int) -> bool:
        """Delete a lead by ID"""
        logger.info(f"Deleting lead with ID: {lead_id}")
        return await self.lead_repository.delete_lead(lead_id)

    async def list_leads(
        self, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = {}
    ) -> Tuple[List[Lead], int]:
        """List leads with pagination and filtering"""
        logger.info(f"Listing leads with skip={skip}, limit={limit}, filters={filters}")

        if filters is None:
            filters = {}

        # Remove None values from filters
        active_filters = {k: v for k, v in filters.items() if v is not None}

        leads, total = await self.lead_repository.get_leads_with_filters(
            skip=skip, limit=limit, filters=active_filters
        )

        return leads, total
