from fastapi import APIRouter, Depends, HTTPException, Request, Header
from app.schemas.lead_schemas import (
    LeadTransferRequest,
    LeadTransferResponse,
    LeadStatus,
)
from app.services.lead_services import create_lead_service
from app.database.appwrite_client import get_appwrite_client
from appwrite.services.databases import Databases
from app.config.settings import settings
from app.auth.jwt_utils import get_current_user, decode_access_token
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.utils.logger import logger
from typing import Optional

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/", response_model=LeadTransferResponse)
@limiter.limit(f"{settings.rate_limit}/minute")
async def create_lead(
    request: Request,
    lead_data: LeadTransferRequest,
    authorization: Optional[str] = Header(None),
):
    """Create a new lead in the system.
    This async function creates a new lead using the provided lead data. It connects to
    the Appwrite database and calls the create_lead_service to perform the actual creation.

    Authorization: Requires a valid Bearer token.

    Args:
        request (Request): The incoming HTTP request.
        lead_data (LeadTransferRequest): Data needed to create a lead.
        authorization (str, optional): The Authorization header.
    Returns:
        dict: The created lead information returned from the create_lead_service.
    Raises:
        HTTPException: If there's an error during lead creation with status code 500.
    """
    # Log request information for debugging
    logger.debug(f"Received lead creation request: {lead_data.model_dump()}")
    logger.debug(f"Authorization header: {authorization}")

    # Force status to ALWAYS be "new" literal string - overriding any enum value
    lead_data_dict = lead_data.model_dump()
    lead_data_dict["status"] = "new"  # Force string literal

    # Create a new lead object with the forced status
    new_lead_data = LeadTransferRequest(**lead_data_dict)

    # Debug logging with detailed type info
    logger.debug(f"Updated lead data with forced status: {new_lead_data.model_dump()}")
    logger.debug(f"Status field type: {type(new_lead_data.status)}")
    logger.debug(f"Status field value: '{new_lead_data.status}'")
    logger.debug(
        f"Status field in dict: '{lead_data_dict['status']}' (type: {type(lead_data_dict['status'])})"
    )

    # Validate the token manually
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Missing or invalid authorization header format")
        logger.debug(f"Raw Authorization header: {authorization}")
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid token. Please include an Authorization header with format: Bearer <token>",
        )

    token = authorization.split(" ")[1]

    # Try to validate token
    try:
        # Try as JWT token first
        try:
            payload = decode_access_token(token)
            logger.debug(f"JWT token validated: {payload}")
        except Exception as e:
            # If JWT validation fails, check if it's the API token
            if token != settings.api_bearer_token:
                logger.warning(f"Invalid token: {str(e)}")
                raise HTTPException(status_code=401, detail="Invalid token")
            else:
                logger.debug("Using API bearer token for authentication")
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Token validation error: {str(e)}")

    try:
        client = get_appwrite_client()
        db = Databases(client)

        # Pass the new_lead_data with forced status instead of original lead_data
        result = await create_lead_service(
            db,
            settings.appwrite_database_id,
            settings.appwrite_leads_collection_id,
            new_lead_data,
        )
        logger.info(f"Lead created: {new_lead_data.email}")
        return result
    except HTTPException as e:
        # Re-raise HTTP exceptions
        logger.error(f"HTTP error creating lead: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error creating lead: {e}")
        # Log more details about the exception
        import traceback

        logger.error(f"Exception traceback: {traceback.format_exc()}")

        # Check for specific external API error patterns
        error_str = str(e)
        if "Internal Server Error" in error_str and "pineapple" in error_str.lower():
            logger.error(f"Pineapple API server error: {error_str}")
            raise HTTPException(
                status_code=502,
                detail=f"Error from Pineapple API: {error_str}. This usually indicates an issue with the data format or API token.",
            )

        # Check for specific Appwrite error messages and provide better context
        if "Missing required attribute" in error_str:
            missing_attr = (
                error_str.split("Missing required attribute")[1].strip().strip('"')
            )
            logger.error(
                f"Appwrite schema error - missing required attribute: {missing_attr}"
            )
            raise HTTPException(
                status_code=400, detail=f"Missing required field: {missing_attr}"
            )

        raise HTTPException(status_code=500, detail=str(e))
