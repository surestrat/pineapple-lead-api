from fastapi import APIRouter, HTTPException, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.schemas.quote import (
    QuoteCreate,
    QuoteResponse,
    QuoteUpdate,
    PineappleQuickQuoteRequest,
    PineappleQuickQuoteResponse,
)
from app.db.repositories.quote_repository import QuoteRepository
from app.db.base import get_async_session
from app.api.quick_quote.service import QuoteService
from app.core.exceptions import NotFoundException, BadRequestException
from app.schemas.pagination import PaginatedResponse, PaginationParams

router = APIRouter()


@router.post(
    "/",
    response_model=QuoteResponse,
    status_code=201,
    summary="Create a new quote",
    description="Creates a new quote for a lead.",
)
async def create_quick_quote(
    quote: QuoteCreate, session: AsyncSession = Depends(get_async_session)
):
    try:
        quote_repository = QuoteRepository(session)
        created_quote = await quote_repository.create_quote(quote)
        return created_quote
    except ValueError as e:
        raise BadRequestException(detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get(
    "/",
    response_model=PaginatedResponse[QuoteResponse],
    summary="List all quotes",
    description="Retrieves a paginated list of quotes with optional filtering.",
)
async def list_quotes(
    pagination: PaginationParams = Depends(),
    lead_id: Optional[int] = Query(None, description="Filter by lead ID"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum quote amount"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum quote amount"),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        quote_repository = QuoteRepository(session)
        quotes, total = await quote_repository.get_quotes_with_filters(
            skip=pagination.skip,
            limit=pagination.limit,
            filters={
                "lead_id": lead_id,
                "min_amount": min_amount,
                "max_amount": max_amount,
            },
        )

        return PaginatedResponse(
            items=quotes, total=total, page=pagination.page, size=pagination.limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get(
    "/{quote_id}",
    response_model=QuoteResponse,
    summary="Get a specific quote",
    description="Retrieves a specific quote by ID.",
)
async def get_quote(
    quote_id: int = Path(..., title="The ID of the quote to retrieve", gt=0),
    session: AsyncSession = Depends(get_async_session),
):
    quote_repository = QuoteRepository(session)
    quote = await quote_repository.get_quote(quote_id)
    if not quote:
        raise NotFoundException(detail=f"Quote with ID {quote_id} not found")
    return quote


@router.put(
    "/{quote_id}",
    response_model=QuoteResponse,
    summary="Update a quote",
    description="Updates an existing quote with new information.",
)
async def update_quote(
    quote_data: QuoteUpdate,
    quote_id: int = Path(..., title="The ID of the quote to update", gt=0),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        quote_repository = QuoteRepository(session)
        updated_quote = await quote_repository.update_quote(quote_id, quote_data)
        if not updated_quote:
            raise NotFoundException(detail=f"Quote with ID {quote_id} not found")
        return updated_quote
    except NotFoundException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.delete(
    "/{quote_id}",
    status_code=204,
    summary="Delete a quote",
    description="Permanently removes a quote from the system.",
)
async def delete_quote(
    quote_id: int = Path(..., title="The ID of the quote to delete", gt=0),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        quote_repository = QuoteRepository(session)
        success = await quote_repository.delete_quote(quote_id)
        if not success:
            raise NotFoundException(detail=f"Quote with ID {quote_id} not found")
        return None
    except NotFoundException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post(
    "/pineapple",
    response_model=PineappleQuickQuoteResponse,
    status_code=201,
    summary="Get a quick quote from Pineapple",
    description="Retrieves a vehicle insurance quote from Pineapple's API.",
)
async def create_pineapple_quote(
    quote_request: PineappleQuickQuoteRequest,
    session: AsyncSession = Depends(get_async_session),
):
    try:
        quote_service = QuoteService(session)
        result = await quote_service.create_pineapple_quote(quote_request)
        return result
    except ValueError as e:
        raise BadRequestException(detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        )
