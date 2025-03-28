"""
Utility to validate and test the API bearer token configuration.

This script helps debug issues with the Pineapple API authentication by testing
different token formats and validating the current environment configuration.
"""

import os
import httpx
import asyncio
import json
from dotenv import load_dotenv
from pathlib import Path


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


def format_token(api_token=None, secret=None):
    """
    Format the API token for Pineapple API.

    Args:
        api_token (str, optional): The API token value. If None, uses environment variable.
        secret (str, optional): The secret value. If None, uses environment variable.

    Returns:
        dict: A dictionary with information about the token formatting
    """
    # Get from environment if not provided
    if api_token is None:
        api_token = os.environ.get("API_BEARER_TOKEN", "")

    if secret is None:
        secret = os.environ.get("SECRET", "")

    result = {
        "has_api_token": bool(api_token),
        "has_secret": bool(secret),
        "token_format": "unknown",
        "formatted_token": "",
        "headers": {},
    }

    if not api_token:
        result["error"] = "API_BEARER_TOKEN is missing"
        return result

    # Check if token already has KEY= and SECRET= format
    if "KEY=" in api_token and "SECRET=" in api_token:
        formatted_token = f"Bearer {api_token}"
        result["token_format"] = "KEY=xxx SECRET=xxx format"
    else:
        # If not in the correct format, try to format it
        if secret:
            formatted_token = f"Bearer KEY={api_token} SECRET={secret}"
            result["token_format"] = "KEY=xxx SECRET=xxx format (composed)"
        else:
            # Try to use as-is
            formatted_token = f"Bearer {api_token}"
            if api_token.startswith("KEY="):
                result["token_format"] = "KEY=xxx format (missing SECRET)"
            else:
                result["token_format"] = "Simple format (not recommended)"
                result["warning"] = "Token doesn't follow KEY/SECRET format"

    result["formatted_token"] = formatted_token
    result["headers"] = {
        "Authorization": formatted_token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # First 10 chars of token for debugging (don't show the whole token)
    if api_token:
        result["token_preview"] = api_token[:10] + "..."

    return result


async def test_pineapple_api_token():
    """
    Test the configured API token against Pineapple API.

    Returns:
        dict: Test results
    """
    # Format the token
    token_info = format_token()

    if "error" in token_info:
        print(f"Error: {token_info['error']}")
        return token_info

    # Get the API base URL
    base_url = os.environ.get("PINEAPPLE_API_BASE_URL", "http://gw.pineapple.co.za")
    lead_endpoint = os.environ.get("PINEAPPLE_LEAD_ENDPOINT", "/users/motor_lead")

    # Prepare a minimal test lead
    test_lead = {
        "source": "API_TEST",
        "first_name": "API",
        "last_name": "Test",
        "email": f"api.test.{int(asyncio.get_event_loop().time())}@example.com",
        "contact_number": "0123456789",
    }

    print(f"Testing API token against: {base_url}{lead_endpoint}")
    print(f"Using token format: {token_info['token_format']}")

    # Make the API call
    results = {
        "token_info": token_info,
        "api_url": f"{base_url}{lead_endpoint}",
        "success": False,
    }

    try:
        # Try to create a lead in Pineapple
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}{lead_endpoint}",
                json=test_lead,
                headers=token_info["headers"],
            )

            results["status_code"] = response.status_code
            results["response_text"] = response.text

            try:
                results["response_json"] = response.json()
            except:
                pass

            if response.status_code == 200 or response.status_code == 201:
                results["success"] = True
                print(f"✅ API token works! Status: {response.status_code}")
                print(f"Response: {response.text[:100]}...")
            else:
                print(f"❌ API token failed! Status: {response.status_code}")
                print(f"Response: {response.text}")

                # Check for specific errors
                if response.status_code == 401:
                    results["error"] = "Authentication failed - invalid token or format"

                    # Check if we need KEY/SECRET format
                    if "KEY=" not in token_info["formatted_token"]:
                        results["suggestion"] = "Try using KEY=xxx SECRET=xxx format"
                elif response.status_code == 400:
                    results["error"] = "Bad request - check lead data format"

    except Exception as e:
        print(f"Error testing API token: {str(e)}")
        results["error"] = str(e)

    return results


if __name__ == "__main__":
    # Print header
    print("\n=== Pineapple API Token Validator ===\n")

    # Print current environment configuration
    print("Current API token configuration:")
    api_token = os.environ.get("API_BEARER_TOKEN", "")
    secret = os.environ.get("SECRET", "")

    if api_token:
        print(f"API_BEARER_TOKEN: {api_token[:10]}... ({len(api_token)} chars)")
    else:
        print("API_BEARER_TOKEN: Not set!")

    if secret:
        print(f"SECRET: {secret[:3]}... ({len(secret)} chars)")
    else:
        print("SECRET: Not set!")

    # Test the token
    print("\nTesting API token against Pineapple API...")
    asyncio.run(test_pineapple_api_token())

    print("\nDone.")
