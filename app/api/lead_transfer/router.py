from fastapi import APIRouter, HTTPException, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.api.lead_transfer.service import LeadTransferService
from app.db.repositories.lead_repository import LeadRepository
from app.db.base import get_async_session
from app.schemas.lead import (
    LeadTransferRequest,
    LeadTransferResponse,
    LeadCreate,
    LeadRead,
    LeadUpdate,
)
from app.core.exceptions import NotFoundException, BadRequestException
from app.schemas.pagination import PaginatedResponse, PaginationParams

router = APIRouter()


@router.post(
    "/transfer",
    response_model=LeadTransferResponse,
    summary="Transfer a lead to a new owner",
    description="Transfers ownership of a lead from one user to another.",
)
async def transfer_lead(
    lead_transfer_request: LeadTransferRequest,
    session: AsyncSession = Depends(get_async_session),
):
    lead_transfer_service = LeadTransferService(session)

    try:
        result = await lead_transfer_service.transfer_lead(lead_transfer_request)
        return result
    except ValueError as e:
        raise BadRequestException(detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get(
    "/",
    response_model=PaginatedResponse[LeadRead],
    summary="List all leads",
    description="Retrieves a paginated list of all leads in the system.",
)
async def list_leads(
    pagination: PaginationParams = Depends(),
    name: Optional[str] = Query(None, description="Filter by lead name"),
    email: Optional[str] = Query(None, description="Filter by lead email"),
    status: Optional[str] = Query(None, description="Filter by lead status"),
    session: AsyncSession = Depends(get_async_session),
):
    lead_transfer_service = LeadTransferService(session)

    try:
        result = await lead_transfer_service.list_leads(
            skip=pagination.skip,
            limit=pagination.limit,
            filters={"name": name, "email": email, "status": status},
        )
        leads = result[0]
        total = result[1] if len(result) > 1 else 0

        return PaginatedResponse(
            items=leads, total=total, page=pagination.page, size=pagination.limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get(
    "/{lead_id}",
    response_model=LeadRead,
    summary="Get a specific lead",
    description="Retrieves detailed information about a specific lead by ID.",
)
async def get_lead(
    lead_id: int = Path(..., title="The ID of the lead to retrieve", gt=0),
    session: AsyncSession = Depends(get_async_session),
):
    lead_transfer_service = LeadTransferService(session)

    try:
        lead = await lead_transfer_service.get_lead(lead_id)
        if not lead:
            raise NotFoundException(detail=f"Lead with ID {lead_id} not found")
        return lead
    except NotFoundException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post(
    "/",
    response_model=LeadRead,
    status_code=201,
    summary="Create a new lead",
    description="Creates a new lead record in the system.",
)
async def create_lead(
    lead_data: LeadCreate, session: AsyncSession = Depends(get_async_session)
):
    lead_transfer_service = LeadTransferService(session)

    try:
        lead = await lead_transfer_service.create_lead(lead_data)
        return lead
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.put(
    "/{lead_id}",
    response_model=LeadRead,
    summary="Update a lead",
    description="Updates information for an existing lead.",
)
async def update_lead(
    lead_data: LeadUpdate,
    lead_id: int = Path(..., title="The ID of the lead to update", gt=0),
    session: AsyncSession = Depends(get_async_session),
):
    lead_transfer_service = LeadTransferService(session)

    try:
        lead = await lead_transfer_service.update_lead(lead_id, lead_data)
        if not lead:
            raise NotFoundException(detail=f"Lead with ID {lead_id} not found")
        return lead
    except NotFoundException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.delete(
    "/{lead_id}",
    status_code=204,
    summary="Delete a lead",
    description="Permanently removes a lead from the system.",
)
async def delete_lead(
    lead_id: int = Path(..., title="The ID of the lead to delete", gt=0),
    session: AsyncSession = Depends(get_async_session),
):
    lead_transfer_service = LeadTransferService(session)

    try:
        success = await lead_transfer_service.delete_lead(lead_id)
        if not success:
            raise NotFoundException(detail=f"Lead with ID {lead_id} not found")
        return None
    except NotFoundException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )
