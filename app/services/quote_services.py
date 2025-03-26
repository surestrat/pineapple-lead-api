import httpx
from fastapi import HTTPException
from app.config.settings import settings
from app.schemas.quote_schemas import QuickQuoteRequest, QuickQuoteResponse
from app.database.appwrite_service import create_quote_document
from appwrite.services.databases import Databases
from app.utils.logger import logger


async def create_quote_service(
    db: Databases, database_id: str, collection_id: str, quote_data: QuickQuoteRequest
) -> QuickQuoteResponse:
    """Create a quote by storing it in Appwrite and sending it to Pineapple API.

    Args:
        db (Databases): The Appwrite database service instance.
        database_id (str): The ID of the Appwrite database.
        collection_id (str): The ID of the Appwrite collection.
        quote_data (QuickQuoteRequest): The quote data to be processed.

    Returns:
        QuickQuoteResponse: The response from the Pineapple API.

    Raises:
        HTTPException: If there's an error with the Pineapple API request or any other processing issue.
    """
    try:
        # First store in Appwrite
        stored_quote = await create_quote_document(
            db, database_id, collection_id, quote_data.model_dump()
        )
        logger.info(f"Quote stored in Appwrite with ID: {stored_quote['$id']}")

        # Prepare API call to Pineapple
        headers = {
            "Authorization": settings.api_bearer_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Then send to Pineapple API with timeout
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                logger.debug(
                    f"Sending request to Pineapple API: {quote_data.model_dump()}"
                )
                response = await client.post(
                    f"{settings.pineapple_api_base_url}{settings.pineapple_quote_endpoint}",
                    json=quote_data.model_dump(),
                    headers=headers,
                )

                # Log response for debugging
                logger.debug(f"Pineapple API response: {response.text}")

                # Handle different response status codes
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
                pineapple_response = QuickQuoteResponse(**response.json())

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

        # Update stored quote with Pineapple response
        try:
            db.update_document(
                database_id=database_id,
                collection_id=collection_id,
                document_id=stored_quote["$id"],
                data={
                    "pineapple_quote_id": pineapple_response.id,
                    "premium": pineapple_response.data[0].premium,
                    "excess": pineapple_response.data[0].excess,
                    "status": "completed",
                },
            )
            logger.info(
                f"Quote updated with Pineapple response: {pineapple_response.id}"
            )
        except Exception as e:
            logger.error(f"Error updating quote in Appwrite: {str(e)}")
            # Continue even if update fails - we have the Pineapple response

        return pineapple_response

    except Exception as e:
        logger.error(f"Error in create_quote_service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
