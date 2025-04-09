from fastapi import APIRouter, Depends, HTTPException, status
from ..models.pineapple_models import (
    LeadTransferRequest,
    LeadTransferResponse,
    QuickQuoteRequest,
    QuickQuoteResponse,
)
from app.services.pineapple_api import PineappleAPIService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["pineapple"])


@router.post(
    "/quick-quote", response_model=QuickQuoteResponse, status_code=status.HTTP_200_OK
)
async def submit_quick_quote(
    quote_request: QuickQuoteRequest,
    pineapple_service: PineappleAPIService = Depends(lambda: PineappleAPIService()),
):
    """
    Submit a vehicle insurance quick quote request to get premium estimate.

    This endpoint forwards the request to Pineapple's API and returns premium and excess information.
    """
    try:
        # Fixed: Use model_dump() instead of dict()
        request_data = quote_request.model_dump()
        logger.debug(f"Processing quick quote request: {request_data}")

        response = pineapple_service.submit_quick_quote(request_data)
        logger.debug(f"Received quick quote response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error processing quick quote: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get insurance quote: {str(e)}",
        )


@router.post(
    "/lead-transfer",
    response_model=LeadTransferResponse,
    status_code=status.HTTP_200_OK,
)
async def transfer_lead(
    lead_request: LeadTransferRequest,
    pineapple_service: PineappleAPIService = Depends(lambda: PineappleAPIService()),
):
    """
    Transfer a lead to Pineapple's system.

    This endpoint forwards lead information to Pineapple and returns a success status and redirect URL.
    """
    try:
        request_data = lead_request.model_dump()
        logger.debug(f"Processing lead transfer request: {request_data}")

        response = pineapple_service.transfer_lead(request_data)
        logger.debug(f"Received lead transfer response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error transferring lead: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transfer lead: {str(e)}",
        )
