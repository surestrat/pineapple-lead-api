from fastapi import HTTPException
import httpx
from appwrite.services.databases import Databases
from app.schemas.lead_schemas import (
    LeadTransferRequest,
    LeadTransferResponse,
    LeadTransferResponseData,
)
from app.database.appwrite_service import create_lead_document
from app.config.settings import settings
from app.utils.logger import logger


async def create_lead_service(
    db: Databases, database_id: str, collection_id: str, lead_data: LeadTransferRequest
) -> LeadTransferResponse:
    """
    Create a new lead in both Appwrite database and Pineapple API.

    Args:
        db: Appwrite Databases service instance
        database_id: ID of the Appwrite database
        collection_id: ID of the Appwrite collection
        lead_data: Lead data to be stored and transferred

    Returns:
        LeadTransferResponse: Response object containing success status and lead data

    Raises:
        HTTPException: If there's an error communicating with Pineapple API or storing in Appwrite
    """
    try:
        # Store lead in Appwrite
        document = await create_lead_document(
            db, database_id, collection_id, lead_data.model_dump()
        )
        logger.info(f"Lead stored in Appwrite with ID: {document['$id']}")

        # Send lead to Pineapple API
        headers = {
            "Authorization": settings.api_bearer_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:

            try:
                logger.debug(f"Sending lead to Pineapple API: {lead_data.model_dump()}")
                response = await client.post(
                    f"{settings.pineapple_api_base_url}{settings.pineapple_lead_endpoint}",
                    json=lead_data.model_dump(),
                    headers=headers,
                )

                logger.debug(f"Pineapple API response: {response.text}")

                if response.status_code == 401:
                    raise HTTPException(
                        status_code=401, detail="Unauthorized access to Pineapple API"
                    )
                elif response.status_code == 400:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Bad request to Pineapple API: {response.text}",
                    )

                response.raise_for_status()

            except httpx.TimeoutException:
                logger.error("Timeout while calling Pineapple API")
                raise HTTPException(
                    status_code=504, detail="Pineapple API request timed out"
                )
            except httpx.RequestError as e:
                logger.error(f"Error calling Pineapple API: {str(e)}")
                raise HTTPException(
                    status_code=502, detail=f"Error calling Pineapple API: {str(e)}"
                )

        return LeadTransferResponse(
            success=True,
            data=LeadTransferResponseData(
                uuid=document["$id"], redirect_url=f"/leads/{document['$id']}"
            ),
        )

    except Exception as e:
        logger.error(f"Error in create_lead_service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
