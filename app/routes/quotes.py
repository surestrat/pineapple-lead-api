from fastapi import APIRouter, Depends, HTTPException, Request
from app.schemas.quote_schemas import QuickQuoteRequest, QuickQuoteResponse
from app.services.quote_services import create_quote_service
from app.auth.jwt_utils import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.utils.logger import logger
from app.database.appwrite_client import get_appwrite_client
from appwrite.services.databases import Databases
from app.config.settings import settings

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/", response_model=QuickQuoteResponse)
@limiter.limit(f"{settings.rate_limit}/minute")
async def create_quote(
    request: Request,
    quote_data: QuickQuoteRequest,
    user: dict = Depends(get_current_user),
):
    """
    Creates a new quote in the database.
    This function handles the creation of a quote by processing the incoming quote data
    and storing it in the Appwrite database. It uses the create_quote_service to handle
    the actual data persistence.
    Args:
        request (Request): The FastAPI request object.
        quote_data (QuickQuoteRequest): The data for the quote to be created.
        user (dict, optional): The authenticated user information obtained from the dependency.
    Returns:
        dict: The result of the quote creation operation.
    Raises:
        HTTPException: If an error occurs during the quote creation process,
                       a 500 status code is returned with the error details.
    """

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
    except Exception as e:
        logger.error(f"Error creating quote: {e}")
        raise HTTPException(status_code=500, detail=str(e))
