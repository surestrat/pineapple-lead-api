"""
Test utility specifically for the Pineapple API.

This script helps diagnose issues with the Pineapple API connection by sending
test leads with different data formats and analyzing responses.
"""

import os
import httpx
import asyncio
import time
import json
from dotenv import load_dotenv
from pathlib import Path
import argparse


# Load environment variables
def load_env_files():
    """Load environment variables from .env files"""
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

    print("No .env file found. Using environment variables only.")
    return False


load_env_files()

# Get configuration
API_BEARER_TOKEN = os.environ.get("API_BEARER_TOKEN", "")
SECRET = os.environ.get("SECRET", "")
PINEAPPLE_API_BASE_URL = os.environ.get(
    "PINEAPPLE_API_BASE_URL", "http://gw.pineapple.co.za"
)
PINEAPPLE_LEAD_ENDPOINT = os.environ.get("PINEAPPLE_LEAD_ENDPOINT", "/users/motor_lead")


def format_token():
    """Format the API token correctly"""
    if not API_BEARER_TOKEN:
        print("Error: API_BEARER_TOKEN is not set in environment variables")
        return None

    # Check if token already has KEY= and SECRET= format
    if "KEY=" in API_BEARER_TOKEN and "SECRET=" in API_BEARER_TOKEN:
        return f"Bearer {API_BEARER_TOKEN}"

    # If SECRET is available, use it
    if SECRET:
        token_value = f"KEY={API_BEARER_TOKEN} SECRET={SECRET}"
        return f"Bearer {token_value}"

    # Otherwise, just return the token as-is with a warning
    print("WARNING: Missing SECRET for API token - this will likely fail!")
    return f"Bearer {API_BEARER_TOKEN}"


async def test_pineapple_api(test_data=None):
    """Test the Pineapple API with different data formats"""
    token = format_token()
    if not token:
        print("Cannot proceed without a properly formatted token")
        return

    if not test_data:
        # Use default test data with more unique values
        import uuid

        unique_id = uuid.uuid4().hex[:8]
        test_data = {
            "source": f"API_TEST_{unique_id}",
            "first_name": "Test",
            "last_name": f"User_{unique_id}",
            "email": f"test.{int(time.time())}.{unique_id}@example.com",
            "contact_number": f"071{unique_id[:7]}",
            "id_number": "",
            "quote_id": "",
        }

    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    url = f"{PINEAPPLE_API_BASE_URL}{PINEAPPLE_LEAD_ENDPOINT}"
    print(f"\nTesting Pineapple API at: {url}")
    print(f"Using data: {json.dumps(test_data, indent=2)}")
    print(
        f"Using token format: {token.split(' ')[0]} {'KEY=' in token}{'SECRET=' in token}"
    )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("\nSending request to Pineapple API...")
            print(f"URL: {url}")
            print(f"Headers: {headers}")
            print(f"Data: {json.dumps(test_data, indent=2)}")

            response = await client.post(
                url,
                json=test_data,
                headers=headers,
            )

            print(f"\nResponse status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")

            # Try to parse as JSON
            try:
                json_response = response.json()
                print(f"Response JSON: {json.dumps(json_response, indent=2)}")
            except:
                print(f"Response text: {response.text}")

            if response.status_code >= 400:
                print("\nRequest failed!")
                if response.status_code == 401:
                    print("Authentication error - check your API token format")
                elif response.status_code == 400:
                    print("Bad request - check your data format")
                elif response.status_code == 500:
                    print("Server error - the API is having issues")

                # Suggest fixes
                if response.status_code in [401, 400]:
                    print("\nSuggested fixes:")
                    print(
                        "1. Make sure your API_BEARER_TOKEN is in the format: KEY=xxx SECRET=xxx"
                    )
                    print("2. Check that the API endpoint URL is correct")
                    print("3. Ensure all required fields have valid values")
            else:
                print("\nRequest successful!")

    except Exception as e:
        print(f"\nError: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the Pineapple API")
    parser.add_argument("--source", default="API_TEST", help="Lead source")
    parser.add_argument("--first_name", default="Test", help="First name")
    parser.add_argument("--last_name", default="User", help="Last name")
    parser.add_argument("--contact", default="0712345678", help="Contact number")

    args = parser.parse_args()

    # Create test data from arguments
    test_data = {
        "source": args.source,
        "first_name": args.first_name,
        "last_name": args.last_name,
        "email": f"test.{int(time.time())}@example.com",
        "contact_number": args.contact,
    }

    # Run the test
    asyncio.run(test_pineapple_api(test_data))
