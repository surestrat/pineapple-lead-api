from appwrite.services.databases import Databases
import json
import time
from datetime import datetime
import logging

# Get the logger for debug purposes
logger = logging.getLogger(__name__)


async def create_lead_document(
    db: Databases, database_id: str, collection_id: str, lead_data: dict
) -> dict:
    """Create a new lead document in the database.
    This function creates a new document in the specified collection of the database
    with the provided lead data.
    Args:
            db (Database): The database instance to use for creating the document.
            database_id (str): The ID of the database where the document will be created.
            collection_id (str): The ID of the collection where the document will be created.
            lead_data (dict): The data for the lead document to be created.
    Returns:
            dict: The created document data returned by the database.
    Raises:
            AppwriteException: If there's an error during document creation.
    """
    # Add extensive logging to help diagnose the issue
    logger.debug(f"Creating lead document with data: {lead_data}")

    # Force status to always be "new" as a simple string
    lead_data["status"] = "new"
    logger.debug(f"Forced status field to 'new' (str)")

    # Double-check required fields
    required_fields = [
        "source",
        "first_name",
        "last_name",
        "email",
        "contact_number",
        "status",
        "created_at",
    ]

    # Create a new clean data dictionary with only the fields we need
    clean_data = {}

    # Ensure each required field is present and properly formatted
    for field in required_fields:
        if field not in lead_data or lead_data[field] is None:
            if field == "status":
                clean_data[field] = "new"
            elif field == "created_at":
                clean_data[field] = datetime.now().isoformat()
            else:
                logger.error(f"Missing required field: {field}")
                raise ValueError(f"Missing required field: {field}")
        else:
            # Convert values to appropriate types
            if field == "status":
                clean_data[field] = "new"  # Always use string literal
            elif field == "created_at":
                if isinstance(lead_data[field], datetime):
                    clean_data[field] = lead_data[field].isoformat()
                else:
                    clean_data[field] = lead_data[field]
            else:
                clean_data[field] = str(lead_data[field])

    # Add optional fields
    if "id_number" in lead_data and lead_data["id_number"]:
        clean_data["id_number"] = str(lead_data["id_number"])
    if "quote_id" in lead_data and lead_data["quote_id"]:
        clean_data["quote_id"] = str(lead_data["quote_id"])

    # Log the final clean data for Appwrite
    logger.debug(f"Final clean data for Appwrite: {clean_data}")
    logger.debug(
        f"Status field in final data: '{clean_data.get('status')}' (type: {type(clean_data.get('status'))})"
    )

    try:
        # Create the document with the clean data
        # Generate a truly unique ID using timestamp and random string
        import uuid
        import time

        unique_id = f"unique_{int(time.time())}_{uuid.uuid4().hex[:8]}"

        document = db.create_document(
            database_id=database_id,
            collection_id=collection_id,
            document_id=unique_id,  # Use our custom unique ID instead of "unique()"
            data=clean_data,
        )
        logger.debug(f"Document created successfully with ID: {document['$id']}")
        return document
    except Exception as e:
        # Enhanced error logging
        logger.error(f"Error creating document in Appwrite: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Data being sent: {clean_data}")
        try:
            # Try to log document structure from Appwrite
            collection = db.get_collection(database_id, collection_id)
            logger.error(f"Collection attributes: {collection.get('attributes', [])}")
        except Exception as col_error:
            logger.error(f"Could not fetch collection info: {str(col_error)}")
        # Re-raise the exception to be handled by the caller
        raise


async def create_quote_document(
    db: Databases, database_id: str, collection_id: str, quote_data: dict
) -> dict:
    """
    Creates a new quote document in the specified Appwrite collection.
    Args:
            db (Database): The Appwrite Database instance to use.
            database_id (str): The ID of the database where the document will be created.
            collection_id (str): The ID of the collection where the document will be created.
            quote_data (dict): The data to be stored in the quote document.
    Returns:
            dict: The created document's data as returned by Appwrite.
    Raises:
            AppwriteException: If there's an error in creating the document.
    """
    # Log the incoming data
    logger.debug(f"Creating quote document with data: {quote_data}")

    # Extract vehicle data - ensure we have it
    vehicles = quote_data.get("vehicles", [])
    if not vehicles:
        logger.error("No vehicles provided in quote data")
        raise ValueError("No vehicles provided in quote data")

    # Serialize vehicles array to JSON string
    vehicles_json = json.dumps(vehicles)

    # Extract key fields for clean storage
    first_vehicle = vehicles[0]
    vehicle_year = first_vehicle.get("year")
    vehicle_make = first_vehicle.get("make")
    vehicle_model = first_vehicle.get("model")
    vehicle_category = first_vehicle.get("category")
    vehicle_use_type = first_vehicle.get("useType")
    vehicle_cover_code = first_vehicle.get("coverCode")
    driver_data = first_vehicle.get("regularDriver", {})

    # Prepare document data ensuring all required fields are present
    document_data = {
        "source": quote_data.get("source"),
        "externalReferenceId": quote_data.get("externalReferenceId"),
        "status": quote_data.get("status", "new"),
        "vehicles_data": vehicles_json,
        "vehicle_year": vehicle_year,
        "vehicle_make": vehicle_make,
        "vehicle_model": vehicle_model,
        "vehicle_category": vehicle_category,
        "vehicle_use_type": vehicle_use_type,
        "vehicle_cover_code": vehicle_cover_code,
        "driver_id_number": driver_data.get("idNumber"),
        "driver_email": driver_data.get("emailAddress"),
        "driver_mobile": driver_data.get("mobileNumber"),
        # Optional fields
        "pineapple_quote_id": quote_data.get("pineapple_quote_id", None),
        "premium": quote_data.get("premium", None),
        "excess": quote_data.get("excess", None),
    }

    # Check if all required fields are present
    required_fields = [
        "source",
        "externalReferenceId",
        "status",
        "vehicles_data",
        "vehicle_year",
        "vehicle_make",
        "vehicle_model",
        "vehicle_category",
        "vehicle_use_type",
        "vehicle_cover_code",
        "driver_id_number",
        "driver_email",
        "driver_mobile",
    ]

    for field in required_fields:
        if field not in document_data or document_data[field] is None:
            logger.error(f"Missing required field: {field}")
            raise ValueError(f"Missing required field: {field} in quote data")

    # Convert enum values to strings
    if not isinstance(document_data["status"], str):
        try:
            if hasattr(document_data["status"], "value"):
                document_data["status"] = str(document_data["status"].value)
            else:
                document_data["status"] = str(document_data["status"])
        except Exception as e:
            logger.warning(f"Error converting status to string: {e}")
            document_data["status"] = "new"  # Safe fallback

    logger.debug(f"Final quote data for Appwrite: {document_data}")

    # Generate a truly unique ID using timestamp and random string
    import uuid
    import time

    unique_id = f"unique_{int(time.time())}_{uuid.uuid4().hex[:8]}"

    return db.create_document(
        database_id=database_id,
        collection_id=collection_id,
        document_id=unique_id,  # Use our custom unique ID instead of "unique()"
        data=document_data,
    )
