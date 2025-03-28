"""
Utility to check Appwrite collection schema for required fields.
This helps debug issues with missing fields that might occur during document creation.
"""

import asyncio
from app.database.appwrite_client import get_appwrite_client
from app.config.settings import settings
from app.utils.logger import logger


async def check_leads_collection_schema():
    """
    Check the schema of the leads collection to verify required fields.
    """
    client = get_appwrite_client()
    try:
        from appwrite.services.databases import Databases

        db = Databases(client)

        # Get collection details
        collection = db.get_collection(
            database_id=settings.appwrite_database_id,
            collection_id=settings.appwrite_leads_collection_id,
        )

        logger.info(f"Checking leads collection schema: {collection['name']}")

        # Extract and display attributes (fields)
        attributes = collection.get("attributes", [])
        logger.info(f"Found {len(attributes)} attributes in schema")

        required_fields = []
        for attr in attributes:
            attr_key = attr.get("key", "unknown")
            attr_required = attr.get("required", False)
            attr_type = attr.get("type", "unknown")

            if attr_required:
                required_fields.append(attr_key)

            logger.debug(
                f"Field '{attr_key}': type={attr_type}, required={attr_required}"
            )

        logger.info(f"Required fields: {', '.join(required_fields)}")

        # Check if status field exists and is required
        status_attribute = next(
            (attr for attr in attributes if attr.get("key") == "status"), None
        )
        if status_attribute:
            logger.info(
                f"Status field exists with type: {status_attribute.get('type')}"
            )
            logger.info(
                f"Status field required: {status_attribute.get('required', False)}"
            )
        else:
            logger.warning("Status field not found in collection schema!")

        return {
            "collection_name": collection["name"],
            "attributes_count": len(attributes),
            "required_fields": required_fields,
            "status_field_exists": status_attribute is not None,
            "status_field_required": (
                status_attribute.get("required", False) if status_attribute else False
            ),
        }

    except Exception as e:
        logger.error(f"Error checking Appwrite schema: {str(e)}")
        return {"error": str(e), "success": False}


if __name__ == "__main__":
    # When run directly, check the schema and print results
    result = asyncio.run(check_leads_collection_schema())
    print("\nResults:")
    for key, value in result.items():
        print(f"{key}: {value}")
