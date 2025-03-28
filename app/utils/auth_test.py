import httpx
import sys
import os
import json
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, date


# Enhanced environment variable loading
def load_env_files():
    """Load environment variables from .env files with proper error handling"""
    # Try standard locations
    locations = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.getcwd(), "app", ".env"),
        os.path.join(Path(__file__).parent.parent.parent, ".env"),
        os.path.join(Path(__file__).parent.parent, ".env"),
    ]

    for loc in locations:
        if os.path.isfile(loc):
            print(f"Loading environment from: {loc}")
            load_dotenv(loc)
            return True

    print("No .env file found in standard locations. Using environment variables only.")
    return False


# Load environment variables
load_env_files()


# Helper function to get environment variables with fallbacks
def get_env(key, default=None):
    """Get an environment variable with support for VITE_ prefix"""
    # Try regular key
    value = os.environ.get(key)
    if value is not None:
        return value

    # Try with VITE_ prefix
    vite_key = f"VITE_{key}"
    value = os.environ.get(vite_key)
    if value is not None:
        print(f"Using VITE_ prefixed value for {key}")
        return value

    # Return default if neither exists
    return default


def get_lead_test_data():
    """Get sample data for lead testing based on Postman examples"""
    return {
        "source": "SureStrat",
        "first_name": "Peter",
        "last_name": "Smith",
        "email": f"peter.smith.{int(datetime.now().timestamp())}@example.com",
        "id_number": "9510025800086",
        "quote_id": "",  # Optional ID of quote
        "contact_number": "0737111119",
    }


def get_quote_test_data():
    """Get sample data for quote testing based on Postman examples"""
    # Use an ISO formatted date for today and a license date 5 years ago
    today = date.today().isoformat()
    license_date = date(
        date.today().year - 5, date.today().month, date.today().day
    ).isoformat()

    return {
        "source": "SureStrat",
        "externalReferenceId": f"TEST{int(datetime.now().timestamp())}",
        "vehicles": [
            {
                "year": 2019,
                "make": "Volkswagen",
                "model": "Polo Tsi 1.2 Comfortline",
                "mmCode": "00815170",
                "modified": "N",
                "category": "HB",
                "colour": "White",
                "engineSize": 1.2,
                "financed": "N",
                "owner": "Y",
                "status": "New",
                "partyIsRegularDriver": "Y",
                "accessories": "Y",
                "accessoriesAmount": 20000,
                "retailValue": 200000,
                "marketValue": 180000,
                "insuredValueType": "Retail",
                "useType": "Private",
                "overnightParkingSituation": "Garage",
                "coverCode": "Comprehensive",
                "address": {
                    "addressLine": "123 Main Street",
                    "postalCode": 2196,
                    "suburb": "Sandton",
                    "latitude": -26.10757,
                    "longitude": 28.0567,
                },
                "regularDriver": {
                    "maritalStatus": "Married",
                    "currentlyInsured": True,
                    "yearsWithoutClaims": 0,
                    "relationToPolicyHolder": "Self",
                    "emailAddress": f"test.driver.{int(datetime.now().timestamp())}@example.com",
                    "mobileNumber": "0821234567",
                    "idNumber": "9404054800086",
                    "prvInsLosses": 0,
                    "licenseIssueDate": license_date,
                    "dateOfBirth": "1994-04-05",
                },
            }
        ],
    }


async def test_auth_flow():
    """
    Test the complete authentication flow:
    1. Get JWT token from /api/v1/auth/token
    2. Use token to call a protected endpoint
    """
    base_url = "http://localhost:8000"

    # Print environment diagnostics
    print("=== Environment Diagnostics ===")
    print(f"TEST_USERNAME: {get_env('TEST_USERNAME')}")
    print(f"TEST_PASSWORD exists: {bool(get_env('TEST_PASSWORD'))}")

    # Step 1: Get the token
    auth_data = {
        "username": get_env("TEST_USERNAME", "test"),
        "password": get_env("TEST_PASSWORD", "test"),
    }

    print(f"Trying to authenticate with username: {auth_data['username']}")

    async with httpx.AsyncClient() as client:
        try:
            auth_response = await client.post(
                f"{base_url}/api/v1/auth/token", json=auth_data
            )

            if auth_response.status_code != 200:
                print(f"Authentication failed with status: {auth_response.status_code}")
                print(f"Response: {auth_response.text}")
                return

            token_data = auth_response.json()
            token = token_data.get("access_token")

            if not token:
                print("No token returned in the response")
                return

            print(f"Authentication successful! Token length: {len(token)}")

            # Step 2: Test the leads endpoint with a Postman-like payload
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            test_lead = get_lead_test_data()

            print("\nTesting leads endpoint with JWT token...")
            lead_response = await client.post(
                f"{base_url}/api/v1/leads", headers=headers, json=test_lead
            )

            print(f"Leads endpoint response status: {lead_response.status_code}")
            print(f"Response: {lead_response.text}")

            # Print headers for debugging
            print("\nRequest headers used:")
            print(json.dumps(dict(headers), indent=2))

            # Step 3: Test the quotes endpoint with a Postman-like payload
            print("\nTesting quotes endpoint with JWT token...")
            test_quote = get_quote_test_data()

            quote_response = await client.post(
                f"{base_url}/api/v1/quotes", headers=headers, json=test_quote
            )

            print(f"Quotes endpoint response status: {quote_response.status_code}")
            print(f"Response: {quote_response.text}")

        except Exception as e:
            print(f"Error during test: {str(e)}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_auth_flow())
