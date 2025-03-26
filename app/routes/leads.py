from fastapi import APIRouter, Depends, HTTPException, Request
from app.schemas.lead_schemas import LeadTransferRequest, LeadTransferResponse
from app.services.lead_services import create_lead_service
from app.database.appwrite_client import get_appwrite_client
from appwrite.services.databases import Databases
from app.config.settings import settings
from app.auth.jwt_utils import get_current_user
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.utils.logger import logger

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/", response_model=LeadTransferResponse)
@limiter.limit(f"{settings.rate_limit}/minute")
async def create_lead(
    request: Request,
    lead_data: LeadTransferRequest,
    user: dict = Depends(get_current_user),
):
    """Create a new lead in the system.
    This async function creates a new lead using the provided lead data. It connects to
    the Appwrite database and calls the create_lead_service to perform the actual creation.
    Args:
        request (Request): The incoming HTTP request.
        lead_data (LeadTransferRequest): Data needed to create a lead.
        user (dict, optional): The authenticated user information. Defaults to Depends(get_current_user).
    Returns:
        dict: The created lead information returned from the create_lead_service.
    Raises:
        HTTPException: If there's an error during lead creation with status code 500.
    """
    try:
        client = get_appwrite_client()
        db = Databases(client)
        result = await create_lead_service(
            db,
            settings.appwrite_database_id,
            settings.appwrite_leads_collection_id,
            lead_data,
        )
        logger.info(f"Lead created: {lead_data.email}")
        return result
    except Exception as e:
        logger.error(f"Error creating lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))
