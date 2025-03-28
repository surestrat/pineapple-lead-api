from fastapi import APIRouter, Depends, HTTPException, Request, Header
from app.schemas.quote_schemas import QuickQuoteRequest, QuickQuoteResponse
from app.services.quote_services import create_quote_service
from app.auth.jwt_utils import get_current_user, decode_access_token
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.utils.logger import logger
from app.database.appwrite_client import get_appwrite_client
from appwrite.services.databases import Databases
from app.config.settings import settings
from typing import Optional

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/", response_model=QuickQuoteResponse)
@limiter.limit(f"{settings.rate_limit}/minute")
async def create_quote(
    request: Request,
    quote_data: QuickQuoteRequest,
    authorization: Optional[str] = Header(None),
):
    """
    Creates a new quote in the database.
    This function handles the creation of a quote by processing the incoming quote data
    and storing it in the Appwrite database. It uses the create_quote_service to handle
    the actual data persistence.
    Args:
        request (Request): The FastAPI request object.
        quote_data (QuickQuoteRequest): The data for the quote to be created.
        authorization (str, optional): The Authorization header.
    Returns:
        dict: The result of the quote creation operation.
    Raises:
        HTTPException: If an error occurs during the quote creation process,
                       a 500 status code is returned with the error details.
    """
    # Log request information for debugging
    logger.debug(f"Received quote creation request: {quote_data.model_dump()}")
    logger.debug(f"Authorization header: {authorization}")

    # Validate the token manually
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Missing or invalid authorization header format")
        raise HTTPException(status_code=401, detail="Missing or invalid token")

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
        result = await create_quote_service(
            db=db,
            database_id=settings.appwrite_database_id,
            collection_id=settings.appwrite_quotes_collection_id,
            quote_data=quote_data,
        )
        logger.info(f"Quote created and stored: {quote_data.externalReferenceId}")
        return result
    except HTTPException as e:
        # Re-raise HTTP exceptions
        logger.error(f"HTTP error creating quote: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error creating quote: {e}")
        # Log more details about the exception
        import traceback

        logger.error(f"Exception traceback: {traceback.format_exc()}")

        # Check for JSON serialization errors
        error_str = str(e)
        if "not JSON serializable" in error_str:
            logger.error(f"JSON serialization error: {error_str}")
            raise HTTPException(
                status_code=500,
                detail="Data formatting error: Some fields cannot be properly serialized. Please ensure dates are in ISO format.",
            )

        raise HTTPException(status_code=500, detail=str(e))
