"""
Simple tool to test API endpoints with authentication.
Run this script directly from the command line.
"""

import httpx
import asyncio
import argparse
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, date


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

# Get API token
API_TOKEN = os.environ.get("API_BEARER_TOKEN")
BASE_URL = "http://localhost:8000"
AUTH_ENDPOINT = "/api/v1/auth/token"
TEST_USERNAME = os.environ.get("TEST_USERNAME", "test")
TEST_PASSWORD = os.environ.get("TEST_PASSWORD", "test")


async def get_auth_token():
    """Get authentication token from API"""
    print(f"Authenticating with username: {TEST_USERNAME}")

    auth_data = {"username": TEST_USERNAME, "password": TEST_PASSWORD}

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BASE_URL}{AUTH_ENDPOINT}", json=auth_data)

        if response.status_code != 200:
            print(f"Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None

        token_data = response.json()
        token = token_data.get("access_token")

        if not token:
            print("No token in response")
            return None

        print(f"Authentication successful! Token obtained.")
        return token


async def test_endpoint(endpoint, data, method="POST"):
    """Test an API endpoint with authentication"""
    # Get auth token
    token = await get_auth_token()

    if not token:
        print("Cannot proceed without authentication token")
        return

    # Set up headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    print(f"\nMaking {method} request to: {endpoint}")
    print(
        f"Headers: {json.dumps({k:v for k,v in headers.items() if k != 'Authorization'})}"
    )
    print(f"Data: {json.dumps(data, indent=2)}")

    # Make the request
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            if method.upper() == "POST":
                response = await client.post(
                    f"{BASE_URL}{endpoint}", json=data, headers=headers
                )
            elif method.upper() == "GET":
                response = await client.get(f"{BASE_URL}{endpoint}", headers=headers)
            else:
                print(f"Unsupported method: {method}")
                return

            print(f"\nResponse status: {response.status_code}")

            try:
                response_data = response.json()
                print(f"Response: {json.dumps(response_data, indent=2)}")
            except:
                print(f"Response: {response.text}")

            return response

        except Exception as e:
            print(f"Error: {str(e)}")
            return None


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


async def test_lead_creation():
    """Test creating a lead using the Postman example data"""
    test_lead = get_lead_test_data()
    await test_endpoint("/api/v1/leads", test_lead)


async def test_quote_creation():
    """Test creating a quote using the Postman example data"""
    test_quote = get_quote_test_data()
    await test_endpoint("/api/v1/quotes", test_quote)


async def run_all_tests():
    """Run both lead and quote tests in sequence"""
    print("=== Testing Lead Creation ===")
    await test_lead_creation()

    print("\n\n=== Testing Quote Creation ===")
    await test_quote_creation()


def main():
    parser = argparse.ArgumentParser(description="Test API endpoints")
    parser.add_argument(
        "--endpoint", "-e", help="API endpoint to test (e.g., /api/v1/leads)"
    )
    parser.add_argument(
        "--method", "-m", default="POST", help="HTTP method (default: POST)"
    )
    parser.add_argument("--file", "-f", help="JSON file with request data")
    parser.add_argument(
        "--lead", action="store_true", help="Run lead test with sample data"
    )
    parser.add_argument(
        "--quote", action="store_true", help="Run quote test with sample data"
    )
    parser.add_argument("--all", action="store_true", help="Run all tests")
    args = parser.parse_args()

    if args.all:
        asyncio.run(run_all_tests())
        return

    if args.lead:
        asyncio.run(test_lead_creation())
        return

    if args.quote:
        asyncio.run(test_quote_creation())
        return

    if not args.endpoint:
        print(
            "Please specify an endpoint with --endpoint or use --lead, --quote, or --all"
        )
        return

    # Load data from file or use default test data
    if args.file and os.path.isfile(args.file):
        with open(args.file, "r") as f:
            data = json.load(f)
    else:
        if "/leads" in args.endpoint:
            data = get_lead_test_data()
        elif "/quotes" in args.endpoint:
            data = get_quote_test_data()
        else:
            data = {}

    asyncio.run(test_endpoint(args.endpoint, data, args.method))


if __name__ == "__main__":
    main()
