"""
Utility for migrating database documents to add missing fields.
"""

import asyncio
from appwrite.services.databases import Databases
from app.database.appwrite_client import get_appwrite_client
from app.config.settings import settings
from datetime import datetime


async def add_status_to_leads():
    """
    Add 'status' field to all lead documents that don't have it.
    """
    print("Starting lead migration to add status field...")

    client = get_appwrite_client()
    db = Databases(client)

    try:
        # Get all leads
        response = db.list_documents(
            database_id=settings.appwrite_database_id,
            collection_id=settings.appwrite_leads_collection_id,
        )

        leads = response["documents"]
        print(f"Found {len(leads)} leads to check")

        updated_count = 0
        for lead in leads:
            # Check if status field is missing
            if "status" not in lead:
                # Update the document
                db.update_document(
                    database_id=settings.appwrite_database_id,
                    collection_id=settings.appwrite_leads_collection_id,
                    document_id=lead["$id"],
                    data={"status": "new"},  # Set status to new for existing leads
                )
                updated_count += 1

            # Also add created_at field if missing
            if "created_at" not in lead:
                db.update_document(
                    database_id=settings.appwrite_database_id,
                    collection_id=settings.appwrite_leads_collection_id,
                    document_id=lead["$id"],
                    data={"created_at": datetime.now().isoformat()},
                )

        print(f"Updated {updated_count} leads with missing status field")

    except Exception as e:
        print(f"Error during migration: {str(e)}")


async def add_status_to_quotes():
    """
    Add 'status' field to all quote documents that don't have it.
    """
    print("Starting quote migration to add status field...")

    client = get_appwrite_client()
    db = Databases(client)

    try:
        # Get all quotes
        response = db.list_documents(
            database_id=settings.appwrite_database_id,
            collection_id=settings.appwrite_quotes_collection_id,
        )

        quotes = response["documents"]
        print(f"Found {len(quotes)} quotes to check")

        updated_count = 0
        for quote in quotes:
            # Check if status field is missing
            if "status" not in quote:
                # Update the document
                db.update_document(
                    database_id=settings.appwrite_database_id,
                    collection_id=settings.appwrite_quotes_collection_id,
                    document_id=quote["$id"],
                    data={"status": "new"},  # Set status to new for existing quotes
                )
                updated_count += 1

            # Also add created_at field if missing
            if "created_at" not in quote:
                db.update_document(
                    database_id=settings.appwrite_database_id,
                    collection_id=settings.appwrite_quotes_collection_id,
                    document_id=quote["$id"],
                    data={"created_at": datetime.now().isoformat()},
                )

        print(f"Updated {updated_count} quotes with missing status field")

    except Exception as e:
        print(f"Error during migration: {str(e)}")


if __name__ == "__main__":
    # Run the migrations
    asyncio.run(add_status_to_leads())
    asyncio.run(add_status_to_quotes())
