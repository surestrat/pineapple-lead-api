"""
Utility for testing API calls directly.
"""

import httpx
import asyncio
import sys
import os
import json
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime


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


async def test_api_call(endpoint, data, token=None):
    """
    Test a direct API call to a specified endpoint.

    Args:
        endpoint (str): API endpoint to call
        data (dict): JSON data to send
        token (str, optional): Bearer token to use
    """
    base_url = "http://localhost:8000"

    # Print environment diagnostics
    print(f"[{datetime.now()}] Environment Diagnostics:")
    print(f"  API_BEARER_TOKEN exists: {bool(get_env('API_BEARER_TOKEN'))}")
    print(f"  TEST_USERNAME: {get_env('TEST_USERNAME')}")

    if not token:
        # First try to get a token
        auth_data = {
            "username": get_env("TEST_USERNAME", "test"),
            "password": get_env("TEST_PASSWORD", "test"),
        }

        print(f"[{datetime.now()}] Getting token with: {auth_data['username']}")

        async with httpx.AsyncClient() as client:
            auth_response = await client.post(
                f"{base_url}/api/v1/auth/token", json=auth_data
            )

            if auth_response.status_code != 200:
                print(
                    f"[{datetime.now()}] Failed to get token: {auth_response.status_code}"
                )
                print(f"Response: {auth_response.text}")
                return

            token_data = auth_response.json()
            token = token_data.get("access_token")

            if not token:
                print(f"[{datetime.now()}] No token returned")
                return

            print(f"[{datetime.now()}] Got token: {token[:10]}...")

    # Now make the actual API call
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    print(f"\n[{datetime.now()}] Making request to: {endpoint}")
    print(f"Headers: {headers}")
    print(f"Data: {json.dumps(data, indent=2)}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{base_url}{endpoint}", json=data, headers=headers
            )

            print(f"\n[{datetime.now()}] Response status: {response.status_code}")
            try:
                response_data = response.json()
                print(f"Response data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"Response text: {response.text}")

            return response

        except Exception as e:
            print(f"[{datetime.now()}] Error making request: {str(e)}")
            return None


async def test_lead_creation():
    """Test creating a lead"""
    test_lead = {
        "source": "TEST",
        "first_name": "Test",
        "last_name": "User",
        "email": f"test{int(datetime.now().timestamp())}@example.com",
        "contact_number": "1234567890",
    }

    await test_api_call("/api/v1/leads", test_lead)


if __name__ == "__main__":
    asyncio.run(test_lead_creation())
