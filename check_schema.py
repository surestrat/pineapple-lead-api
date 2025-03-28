"""
Utility to check the Appwrite database schema and validate field requirements.
This is helpful for diagnosing issues with missing required fields.
"""

import os

import sys
import time
import json
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.users import Users
from pathlib import Path


# Load environment variables
def load_env():
    locations = [
        ".env",
        "app/.env",
        os.path.join(Path(__file__).parent, ".env"),
        os.path.join(Path(__file__).parent, "app", ".env"),
    ]

    for loc in locations:
        if os.path.isfile(loc):
            print(f"Loading environment from: {loc}")
            load_dotenv(loc)
            return True

    print("No .env file found. Using environment variables only.")
    return False


load_env()

# Initialize Appwrite client
client = Client()
client.set_endpoint(os.environ.get("APPWRITE_ENDPOINT"))
client.set_project(os.environ.get("APPWRITE_PROJECT_ID"))
client.set_key(os.environ.get("APPWRITE_API_KEY"))

# Initialize services
db = Databases(client)
users = Users(client)

# Get configuration values
database_id = os.environ.get("APPWRITE_DATABASE_ID")
leads_collection_id = os.environ.get("APPWRITE_LEADS_COLLECTION_ID")
quotes_collection_id = os.environ.get("APPWRITE_QUOTES_COLLECTION_ID")


def check_collection_schema(collection_id, name):
    """Check and display the schema for a collection"""
    print(f"\n==== {name} Collection Schema ====")

    if database_id is None:
        print("Error: database_id is None")
        return

    try:
        # Get collection info
        collection = db.get_collection(database_id, collection_id)
        print(f"Collection Name: {collection['name']}")
        print(f"Collection ID: {collection['$id']}")

        # Get attributes (fields)
        attributes = collection.get("attributes", [])
        print(f"\nTotal Attributes: {len(attributes)}")

        # Print details of each attribute
        for attr in attributes:
            attr_type = attr.get("type", "unknown")
            attr_key = attr.get("key", "unknown")
            attr_required = attr.get("required", False)
            attr_default = attr.get("default", "None")

            print(f"\n{attr_key}:")
            print(f"  Type: {attr_type}")
            print(f"  Required: {attr_required}")
            print(f"  Default: {attr_default}")

            # Check for array items
            if attr_type == "array":
                items = attr.get("items", [])
                if items:
                    print(f"  Array Items: {items}")

            # Check for enum values
            if attr_type == "enum":
                elements = attr.get("elements", [])
                if elements:
                    print(f"  Enum Values: {elements}")

        # Print required fields
        required_fields = [
            attr.get("key") for attr in attributes if attr.get("required", False)
        ]
        print(f"\nRequired Fields: {required_fields}")
    except Exception as e:
        print(f"Error retrieving collection schema: {str(e)}")


def create_test_lead():
    """Create a test lead with minimal fields to test schema requirements"""
    print("\n==== Creating Test Lead ====")

    from datetime import datetime

    test_lead = {
        "source": "TEST_SCHEMA",
        "first_name": "Schema",
        "last_name": "Test",
        "email": f"schema.test.{int(time.time())}@example.com",
        "contact_number": "1234567890",
        "status": "new",
        "created_at": datetime.now().isoformat(),
    }

    if database_id is None:
        print("Error: database_id is None")
        return

    if leads_collection_id is None:
        print("Error: leads_collection_id is None")
        return

    try:
        document = db.create_document(
            database_id=database_id,
            collection_id=leads_collection_id,
            document_id="unique()",
            data=test_lead,
        )
        print(f"Test lead created successfully with ID: {document['$id']}")
        print(f"Fields in created document: {list(document.keys())}")
    except Exception as e:
        print(f"Error creating test lead: {str(e)}")


def check_recently_created_leads():
    """Check the most recently created leads to debug issues"""
    print("\n==== Recently Created Leads ====")

    if database_id is None:
        print("Error: database_id is None")
        return

    if leads_collection_id is None:
        print("Error: leads_collection_id is None")
        return

    try:
        # Use proper Appwrite query format - 'limit(5)' instead of 'orderDesc'
        # which seems to be causing the "Invalid query: Syntax error"
        leads = db.list_documents(
            database_id=database_id,
            collection_id=leads_collection_id,
            queries=["limit(5)"],
        )

        print(f"Found {len(leads['documents'])} recent leads")

        for i, lead in enumerate(leads["documents"]):
            print(f"\nLead #{i+1}:")
            print(f"  ID: {lead['$id']}")
            print(f"  Created At: {lead.get('$createdAt', 'MISSING!')}")
            print(f"  Status: {lead.get('status', 'MISSING!')}")
            print(f"  Email: {lead.get('email', 'MISSING!')}")
            print(f"  Available Fields: {list(lead.keys())}")

            # Check for required fields
            missing = []
            for field in [
                "status",
                "source",
                "first_name",
                "last_name",
                "email",
                "contact_number",
                "created_at",
            ]:
                if field not in lead:
                    missing.append(field)

            if missing:
                print(f"  Missing Fields: {missing}")
            else:
                print("  All important fields present!")

    except Exception as e:
        print(f"Error checking recent leads: {str(e)}")
        # Print the full error traceback for better debugging
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("Appwrite Database Schema Check Tool")
    print("==================================")

    if not database_id or not leads_collection_id:
        print("Error: Missing database or collection IDs in environment")
        sys.exit(1)

    # Check leads collection schema
    check_collection_schema(leads_collection_id, "Leads")

    # Check quotes collection schema
    if quotes_collection_id:
        check_collection_schema(quotes_collection_id, "Quotes")

    # Check recent leads
    check_recently_created_leads()

    print("\nSchema check complete")
