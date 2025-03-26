from appwrite.services.databases import Databases
import json
import time


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

    return db.create_document(
        database_id=database_id,
        collection_id=collection_id,
        document_id="unique()",
        data=lead_data,
    )


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
    # Serialize vehicles array to JSON string
    vehicles_json = json.dumps(quote_data.get("vehicles", []))

    # Extract key fields for clean storage
    first_vehicle = (
        quote_data.get("vehicles", [])[0] if quote_data.get("vehicles") else {}
    )
    vehicle_year = first_vehicle.get("year")
    vehicle_make = first_vehicle.get("make")
    vehicle_model = first_vehicle.get("model")
    vehicle_category = first_vehicle.get("category")
    vehicle_use_type = first_vehicle.get("useType")
    vehicle_cover_code = first_vehicle.get("coverCode")
    driver_data = first_vehicle.get("regularDriver", {})

    # Prepare document data
    document_data = {
        "source": quote_data.get("source"),
        "externalReferenceId": quote_data.get("externalReferenceId"),
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
        "status": "pending",
    }

    return db.create_document(
        database_id=database_id,
        collection_id=collection_id,
        document_id="unique()",
        data=document_data,
    )
