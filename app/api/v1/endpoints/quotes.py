import logging
import uuid
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
    BackgroundTasks,
)

from app.api import deps
from app.schemas import quote as quote_schema
from app.schemas import user as user_schema
from app.services.pineapple_api import get_quick_quote
from app.models.pineapple import QuickQuoteRequest, QuickQuoteResponse
from app.core.config import settings
from app.crud import crud_quote
from supabase import Client
from app.main import limiter

logger = logging.getLogger(__name__)
router = APIRouter()


async def update_quote_record_background(
    db: Client, local_quote_id: str, update_data: quote_schema.QuoteRecordUpdate
):
    """Task to update quote record in the background."""
    logger.info(
        f"[BG Task] Updating quote record {local_quote_id} with status {update_data.status}..."
    )
    try:
        updated = crud_quote.update_quote_record(
            db=db, local_quote_id=local_quote_id, quote_update_data=update_data
        )
        if updated:
            logger.info(
                f"[BG Task] Quote record {local_quote_id} update finished successfully."
            )
        else:
            logger.error(
                f"[BG Task] Failed to update quote record {local_quote_id} (CRUD returned None/False)."
            )
    except Exception as e:
        logger.exception(
            f"[BG Task] Exception during quote record {local_quote_id} update: {e}"
        )


@router.post(
    "/quick",
    response_model=quote_schema.QuoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Request a Quick Insurance Quote",
    description="Submits vehicle details to get a quote from the external Pineapple provider. Stores request/response locally.",
    responses={
        status.HTTP_502_BAD_GATEWAY: {
            "description": "External API (Pineapple) failure"
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal database or processing error"
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid authentication credentials"
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Rate limit exceeded"},
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid input data (though Pydantic catches most)"
        },
    },
)
@limiter.limit("30/minute")
async def request_quick_quote(
    *,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Client = Depends(deps.get_db),
    current_user: user_schema.User = Depends(deps.get_current_user),
    quote_input: quote_schema.QuoteRequest,
):
    """
    Requests a quick insurance quote:
    1. Creates a local record for the quote request attempt.
    2. Calls the external Pineapple Quick Quote API.
    3. Returns the quote result from Pineapple (including `quote_id` needed for lead transfer).
    4. Updates the local quote record status in the background.
    """
    endpoint_log_ref = f"user_id={current_user.id}"
    logger.info(f"Quote request received from {endpoint_log_ref}")
    local_quote_ref_id = str(uuid.uuid4())
    pineapple_client = request.app.state.pineapple_client

    logger.debug(
        f"Creating initial quote record {local_quote_ref_id} for {endpoint_log_ref}"
    )
    quote_record_in = quote_schema.QuoteRecordCreate(
        id=local_quote_ref_id,
        user_id=str(current_user.id),
        request_details=quote_input.model_dump(),
        status="pending_external",
    )
    created_record_dict = crud_quote.create_quote_record(
        db=db, quote_in=quote_record_in
    )
    if not created_record_dict:
        logger.error(
            f"Failed to create initial quote record in DB for {endpoint_log_ref}, ref {local_quote_ref_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save quote request internally before contacting provider.",
        )
    local_quote_ref_id = created_record_dict.get("id", local_quote_ref_id)
    logger.info(
        f"Initial quote record {local_quote_ref_id} created for {endpoint_log_ref}"
    )

    pineapple_vehicles = [
        quote_schema.PineappleVehicle.model_validate(vehicle.model_dump())
        for vehicle in quote_input.vehicles
    ]

    pineapple_request = quote_schema.PineappleQuickQuoteRequest(
        source=settings.PINEAPPLE_SOURCE_NAME,
        externalReferenceId=local_quote_ref_id,
        vehicles=pineapple_vehicles,
    )
    pineapple_response = get_quick_quote(pineapple_request.model_dump())

    update_data = quote_schema.QuoteRecordUpdate()
    response_payload: quote_schema.QuoteResponse | None = None

    if (
        pineapple_response["success"]
        and pineapple_response["id"]
        and pineapple_response["data"]
    ):
        pineapple_quote_id = pineapple_response["id"]
        logger.info(
            f"Successfully obtained quote {pineapple_quote_id} from Pineapple for local ref {local_quote_ref_id}"
        )
        update_data.status = "success"
        update_data.pineapple_quote_id = pineapple_quote_id
        update_data.response_details = pineapple_response
        update_data.premium = pineapple_response["data"][0]["premium"]
        update_data.excess = pineapple_response["data"][0]["excess"]

        response_payload = quote_schema.QuoteResponse(
            success=True,
            quote_id=pineapple_quote_id,
            quote_data=[
                quote_schema.QuoteResponseData.model_validate(item)
                for item in pineapple_response["data"]
            ],
            local_quote_reference_id=local_quote_ref_id,
            message="Quote retrieved successfully.",
        )
        background_tasks.add_task(
            update_quote_record_background, db, local_quote_ref_id, update_data
        )
        logger.info(
            f"Scheduled background task to update quote record {local_quote_ref_id} with success status."
        )

        return response_payload

    else:
        error_msg = (
            pineapple_response.get("message", "")
            or "Unknown failure from external quote provider."
        )
        logger.error(
            f"Failed to get quote from Pineapple for local ref {local_quote_ref_id}. Reason: {error_msg}"
        )
        update_data.status = "failed_external"
        update_data.error_message = error_msg
        update_data.response_details = pineapple_response

        background_tasks.add_task(
            update_quote_record_background, db, local_quote_ref_id, update_data
        )
        logger.info(
            f"Scheduled background task to update quote record {local_quote_ref_id} with failure status."
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to get quote from external provider: {error_msg}",
        )

    logger.error(
        f"Reached end of quote endpoint unexpectedly for {endpoint_log_ref}, ref {local_quote_ref_id}"
    )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Internal processing error.",
    )


@router.post(
    "/quick-quote", response_model=QuickQuoteResponse, status_code=status.HTTP_200_OK
)
async def create_quick_quote(
    quote_request: QuickQuoteRequest,
    current_user: user_schema.User = Depends(deps.get_current_user),
):
    """
    Submit a vehicle insurance quick quote request to get premium estimate.

    This endpoint forwards the request to Pineapple's API and returns premium information.
    """
    try:
        response = get_quick_quote(quote_request.model_dump())
        return response
    except Exception as e:
        logger.error(f"Error processing quick quote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get insurance quote: {str(e)}",
        )
