from fastapi import HTTPException
import httpx
import os
from appwrite.services.databases import Databases
from app.schemas.lead_schemas import (
    LeadTransferRequest,
    LeadTransferResponse,
    LeadTransferResponseData,
    LeadStatus,
)
from app.database.appwrite_service import create_lead_document
from app.config.settings import settings
from app.utils.logger import logger
from app.utils.json_utils import to_json  # Import the new utility
from datetime import datetime


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
        # Prepare lead data for Appwrite storage
        lead_dict = lead_data.model_dump()

        # Explicitly force the status field to ensure it's present and properly formatted
        lead_dict["status"] = "new"  # Always use a plain string literal

        # Extra debug logging for status field
        logger.debug(
            f"Setting status field explicitly to 'new' (type: {type(lead_dict['status'])})"
        )

        # Ensure all required fields are present according to Appwrite schema
        required_fields = [
            "source",
            "first_name",
            "last_name",
            "email",
            "contact_number",
            "status",
            "created_at",
        ]

        # Add created_at if not present
        if "created_at" not in lead_dict or lead_dict["created_at"] is None:
            lead_dict["created_at"] = datetime.now().isoformat()
        elif isinstance(lead_dict["created_at"], datetime):
            lead_dict["created_at"] = lead_dict["created_at"].isoformat()

        # Double check all fields are present and properly typed
        for field in required_fields:
            if field not in lead_dict or lead_dict[field] is None:
                if field == "status":
                    lead_dict[field] = "new"
                elif field == "created_at":
                    lead_dict[field] = datetime.now().isoformat()
                else:
                    logger.error(f"Missing required field after validation: {field}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Missing required field: {field}",
                    )

        # Log detailed information about the lead data to diagnose issues
        logger.debug(f"Lead data keys before storing: {lead_dict.keys()}")
        logger.debug(
            f"Status field value: '{lead_dict['status']}' (type: {type(lead_dict['status'])})"
        )
        logger.debug(f"Full lead data structure: {lead_dict}")

        # Store lead in Appwrite with explicit schema checking
        try:
            # Create a clean, simplified document that meets Appwrite schema requirements
            clean_data = {
                "source": str(lead_dict["source"]),
                "first_name": str(lead_dict["first_name"]),
                "last_name": str(lead_dict["last_name"]),
                "email": str(lead_dict["email"]),
                "contact_number": str(lead_dict["contact_number"]),
                "status": "new",  # Explicitly set as string literal
                "created_at": lead_dict["created_at"],
            }

            # Add optional fields if present
            if lead_dict.get("id_number"):
                clean_data["id_number"] = str(lead_dict["id_number"])
            if lead_dict.get("quote_id"):
                clean_data["quote_id"] = str(lead_dict["quote_id"])

            logger.debug(f"Clean document data being sent to Appwrite: {clean_data}")

            document = await create_lead_document(
                db, database_id, collection_id, clean_data
            )
            logger.info(f"Lead stored in Appwrite with ID: {document['$id']}")
            logger.debug(f"Stored document data: {document}")
        except Exception as doc_error:
            logger.error(f"Error creating document in Appwrite: {str(doc_error)}")
            logger.error(f"Failed payload: {lead_dict}")
            raise

        # Format the authorization token in the correct format for Pineapple API
        # Get the token directly from settings to ensure it's always present
        api_token = settings.api_bearer_token
        secret = os.environ.get("SECRET", "")

        # IMPORTANT FIX: Ensure token is properly formatted for Pineapple API
        if not api_token:
            logger.error("API_BEARER_TOKEN is missing in environment variables!")
            raise HTTPException(
                status_code=500,
                detail="API configuration error - missing API credentials",
            )

        # New token formatting logic - explicitly build the correct format
        # Don't use any prefix like "Bearer" - the httpx client will add it
        if "KEY=" in api_token and "SECRET=" in api_token:
            # Token already has proper format - use as is
            token = api_token
            logger.debug("Using pre-formatted API token with KEY and SECRET")
        else:
            # Need to build the proper format
            if secret:
                # Create the proper format with separate KEY and SECRET
                token = f"KEY={api_token} SECRET={secret}"
                logger.debug("Created properly formatted token with KEY and SECRET")
            else:
                logger.error("SECRET environment variable is missing!")
                raise HTTPException(
                    status_code=500,
                    detail="API configuration error - missing SECRET for API token",
                )

        # Log token format for debugging (without exposing actual values)
        token_format = "Unknown format"
        if "KEY=" in token and "SECRET=" in token:
            token_format = "KEY=xxx SECRET=xxx format"
        else:
            token_format = "Improperly formatted token - missing KEY or SECRET part"
            logger.warning("Token is not properly formatted with KEY and SECRET parts")

        logger.debug(f"Using token format: {token_format}")

        # Add "Bearer" prefix for the Authorization header
        auth_header = f"Bearer {token}"

        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Serialize the lead data properly, handling any date fields
                # Remove status field for Pineapple API request as it's only needed for Appwrite
                api_lead_data = {
                    k: v
                    for k, v in lead_data.model_dump().items()
                    if k not in ["status", "created_at"]
                }

                # Ensure all required fields have valid values for Pineapple API
                for field in [
                    "source",
                    "first_name",
                    "last_name",
                    "email",
                    "contact_number",
                ]:
                    if not api_lead_data.get(field) or api_lead_data[field] == "string":
                        logger.warning(
                            f"Field '{field}' has generic value: '{api_lead_data.get(field)}'"
                        )
                        if field == "email":
                            # Generate a unique email to avoid duplicates
                            import time

                            api_lead_data[field] = (
                                f"test.{int(time.time())}@example.com"
                            )
                            logger.info(
                                f"Replaced generic email with: {api_lead_data[field]}"
                            )

                lead_json = to_json(api_lead_data)

                logger.debug(f"Sending lead to Pineapple API: {lead_json}")
                logger.debug(f"Authorization header format: {token_format}")
                logger.debug(
                    f"API URL: {settings.pineapple_api_base_url}{settings.pineapple_lead_endpoint}"
                )

                response = await client.post(
                    f"{settings.pineapple_api_base_url}{settings.pineapple_lead_endpoint}",
                    content=lead_json,  # Use pre-serialized JSON content
                    headers=headers,
                )

                logger.debug(f"Pineapple API response status: {response.status_code}")
                logger.debug(f"Pineapple API response: {response.text}")

                # Try to get JSON response
                response_json = None
                try:
                    response_json = response.json()
                    logger.debug(f"Pineapple API JSON response: {response_json}")
                except:
                    logger.warning("Could not parse response as JSON")

                # Handle specific error cases
                if response.status_code >= 400:
                    error_msg = f"Pineapple API error: {response.status_code}"
                    if response_json and isinstance(response_json, dict):
                        error_detail = response_json.get(
                            "message", response_json.get("error", "Unknown error")
                        )
                        error_msg = f"{error_msg} - {error_detail}"
                    else:
                        error_msg = f"{error_msg} - {response.text}"

                    logger.error(error_msg)

                    # Store the error details in Appwrite for reference
                    try:
                        db.update_document(
                            database_id=database_id,
                            collection_id=collection_id,
                            document_id=document["$id"],
                            data={
                                "status": LeadStatus.FAILED.value,
                                "error_details": error_msg[:500],  # Limit length
                            },
                        )
                    except Exception as update_error:
                        logger.warning(
                            f"Failed to update lead with error details: {update_error}"
                        )

                    if response.status_code == 401:
                        raise HTTPException(
                            status_code=401,
                            detail=f"Unauthorized access to Pineapple API: {error_msg}",
                        )
                    elif response.status_code == 400:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Bad request to Pineapple API: {error_msg}",
                        )
                    elif response.status_code == 500:
                        raise HTTPException(
                            status_code=502,
                            detail=f"Pineapple API server error: {error_msg}",
                        )
                    else:
                        raise HTTPException(
                            status_code=response.status_code, detail=error_msg
                        )

                response.raise_for_status()

                # Update status to PENDING when sending to Pineapple API
                try:
                    db.update_document(
                        database_id=database_id,
                        collection_id=collection_id,
                        document_id=document["$id"],
                        data={"status": LeadStatus.PENDING.value},
                    )
                    logger.info(
                        f"Lead status updated to 'pending' for ID: {document['$id']}"
                    )
                except Exception as update_error:
                    logger.warning(f"Failed to update lead status: {update_error}")

                # Update lead status in Appwrite based on successful API response
                try:
                    db.update_document(
                        database_id=database_id,
                        collection_id=collection_id,
                        document_id=document["$id"],
                        data={"status": LeadStatus.COMPLETED.value},
                    )
                    logger.info(
                        f"Lead status updated to 'completed' for ID: {document['$id']}"
                    )
                except Exception as update_error:
                    logger.warning(f"Failed to update lead status: {update_error}")
                    # Continue execution even if status update fails

            except httpx.HTTPStatusError as e:
                # Already handled above with custom error messages
                raise
            except httpx.TimeoutException:
                # Update status to FAILED on timeout
                try:
                    db.update_document(
                        database_id=database_id,
                        collection_id=collection_id,
                        document_id=document["$id"],
                        data={"status": LeadStatus.FAILED.value},
                    )
                except Exception:
                    pass  # Ignore error if update fails

                logger.error("Timeout while calling Pineapple API")
                raise HTTPException(
                    status_code=504, detail="Pineapple API request timed out"
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
