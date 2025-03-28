import httpx
import os
from datetime import date, datetime
from fastapi import HTTPException
from app.config.settings import settings
from app.schemas.quote_schemas import QuickQuoteRequest, QuickQuoteResponse, QuoteStatus
from app.database.appwrite_service import create_quote_document
from appwrite.services.databases import Databases
from app.utils.logger import logger
from app.utils.json_utils import to_json  # Import the new utility


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
        # Add status if not already present
        quote_dict = quote_data.model_dump()
        if "status" not in quote_dict:
            quote_dict["status"] = QuoteStatus.NEW.value

        # Validate that we have all required fields for Appwrite based on the schema
        if not quote_dict.get("vehicles"):
            logger.error("No vehicles provided in quote data")
            raise HTTPException(
                status_code=400, detail="No vehicles provided in quote data"
            )

        first_vehicle = quote_dict["vehicles"][0]
        driver = first_vehicle.get("regularDriver", {})

        # Check if all key fields are present
        required_vehicle_fields = {
            "year": "vehicle year",
            "make": "vehicle make",
            "model": "vehicle model",
            "category": "vehicle category",
            "useType": "vehicle use type",
            "coverCode": "vehicle cover code",
        }

        required_driver_fields = {
            "idNumber": "driver ID number",
            "emailAddress": "driver email",
            "mobileNumber": "driver mobile",
        }

        missing_fields = []
        for field, description in required_vehicle_fields.items():
            if field not in first_vehicle or first_vehicle[field] is None:
                missing_fields.append(description)

        for field, description in required_driver_fields.items():
            if field not in driver or driver[field] is None:
                missing_fields.append(description)

        if not quote_dict.get("source"):
            missing_fields.append("source")

        if not quote_dict.get("externalReferenceId"):
            missing_fields.append("external reference ID")

        if missing_fields:
            logger.error(f"Missing required fields for quote: {missing_fields}")
            raise HTTPException(
                status_code=400,
                detail=f"Missing required fields: {', '.join(missing_fields)}",
            )

        # First store in Appwrite
        stored_quote = await create_quote_document(
            db, database_id, collection_id, quote_dict
        )
        logger.info(f"Quote stored in Appwrite with ID: {stored_quote['$id']}")

        # Format the authorization token in the correct format for Pineapple API
        # Get the token directly from settings to ensure it's always present
        api_token = settings.api_bearer_token
        secret = os.environ.get("SECRET", "")

        # Ensure we have a properly formatted token
        if not api_token:
            logger.error("API_BEARER_TOKEN is missing in environment variables!")
            raise HTTPException(
                status_code=500,
                detail="API configuration error - missing API credentials",
            )

        # Check if token already has KEY= and SECRET= format
        if "KEY=" in api_token and "SECRET=" in api_token:
            token = f"Bearer {api_token}"
            logger.debug("Using pre-formatted API token with KEY and SECRET")
        else:
            # If not in the correct format, try to format it
            if secret:
                token = f"Bearer KEY={api_token} SECRET={secret}"
                logger.debug("Formatted API token using separate SECRET")
            else:
                # Check for KEY= prefix
                if not api_token.startswith("KEY="):
                    # Last resort - try to use token as-is
                    token = f"Bearer {api_token}"
                    logger.warning(
                        "Using API token without KEY/SECRET format - this may fail!"
                    )
                else:
                    # Token has just the KEY part
                    token = f"Bearer {api_token}"
                    logger.warning(
                        "Using API token with only KEY format - missing SECRET!"
                    )

        # Log token format (but not the actual token) for debugging
        token_format = "Unknown format"
        if "KEY=" in token and "SECRET=" in token:
            token_format = "KEY=xxx SECRET=xxx format"
        elif "KEY=" in token:
            token_format = "KEY=xxx format (missing SECRET)"
        elif token.startswith("Bearer "):
            token_format = "Simple Bearer format"

        logger.debug(f"Using authorization token in {token_format}")

        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Then send to Pineapple API with timeout
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Update status to PENDING when sending to Pineapple API
                try:
                    db.update_document(
                        database_id=database_id,
                        collection_id=collection_id,
                        document_id=stored_quote["$id"],
                        data={"status": QuoteStatus.PENDING.value},
                    )
                    logger.info(
                        f"Quote status updated to 'pending' for ID: {stored_quote['$id']}"
                    )
                except Exception as update_error:
                    logger.warning(f"Failed to update quote status: {update_error}")

                # Serialize the model data with date support using our utility
                # Send only the necessary fields to Pineapple API (remove status and created_at)
                api_quote_data = {
                    key: value
                    for key, value in quote_dict.items()
                    if key not in ["status", "created_at"]
                }

                # Use our to_json utility to handle date serialization
                quote_json = to_json(api_quote_data)

                logger.debug(f"Sending request to Pineapple API: {quote_json[:200]}...")

                response = await client.post(
                    f"{settings.pineapple_api_base_url}{settings.pineapple_quote_endpoint}",
                    content=quote_json,  # Use pre-serialized JSON content
                    headers=headers,
                )

                # Log response for debugging
                logger.debug(f"Pineapple API response: {response.text}")

                # Handle different response status codes
                if response.status_code == 401:
                    # Update document status to failed
                    db.update_document(
                        database_id=database_id,
                        collection_id=collection_id,
                        document_id=stored_quote["$id"],
                        data={"status": QuoteStatus.FAILED.value},
                    )
                    raise HTTPException(
                        status_code=401, detail="Unauthorized access to Pineapple API"
                    )
                elif response.status_code == 400:
                    # Update document status to failed
                    db.update_document(
                        database_id=database_id,
                        collection_id=collection_id,
                        document_id=stored_quote["$id"],
                        data={"status": QuoteStatus.FAILED.value},
                    )
                    raise HTTPException(
                        status_code=400,
                        detail=f"Bad request to Pineapple API: {response.text}",
                    )

                response.raise_for_status()
                pineapple_response = QuickQuoteResponse(**response.json())

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
                            "status": QuoteStatus.COMPLETED.value,
                        },
                    )
                    logger.info(
                        f"Quote updated with Pineapple response: {pineapple_response.id}"
                    )
                except Exception as e:
                    logger.error(f"Error updating quote in Appwrite: {str(e)}")
                    # Continue even if update fails - we have the Pineapple response

            except httpx.TimeoutException:
                # Update document status to failed
                db.update_document(
                    database_id=database_id,
                    collection_id=collection_id,
                    document_id=stored_quote["$id"],
                    data={"status": QuoteStatus.FAILED.value},
                )

                logger.error("Timeout while calling Pineapple API")
                raise HTTPException(
                    status_code=504, detail="Pineapple API request timed out"
                )
            except httpx.RequestError as e:
                # Update document status to failed
                db.update_document(
                    database_id=database_id,
                    collection_id=collection_id,
                    document_id=stored_quote["$id"],
                    data={"status": QuoteStatus.FAILED.value},
                )

                logger.error(f"Error calling Pineapple API: {str(e)}")
                raise HTTPException(
                    status_code=502, detail=f"Error calling Pineapple API: {str(e)}"
                )

        return pineapple_response

    except Exception as e:
        logger.error(f"Error in create_quote_service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
