"""
Utility for debugging JWT tokens.
This script can be run directly to verify and decode tokens.
"""

import sys
import jwt
import os
from dotenv import load_dotenv
from pathlib import Path


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


def decode_jwt(token_string, print_result=True):
    """Decode and verify a JWT token string."""
    # Get secret using our enhanced function
    secret_key = get_env("SECRET_KEY")
    algorithm = get_env("ALGORITHM", "HS256")

    if not secret_key:
        print("ERROR: SECRET_KEY not found in environment variables")
        return None

    try:
        # First try without verification (just decode)
        header = jwt.get_unverified_header(token_string)
        print(f"Token header: {header}")

        # Now try to properly decode and verify
        decoded = jwt.decode(token_string, secret_key, algorithms=[algorithm])

        if print_result:
            print("\n=== JWT Token Verified Successfully ===")
            print(f"Algorithm: {header.get('alg')}")
            print(f"Type: {header.get('typ')}")
            print("\nPayload:")
            for key, value in decoded.items():
                print(f"  {key}: {value}")
            print("\n=== Token Valid ===")

        return decoded
    except jwt.ExpiredSignatureError:
        print("ERROR: Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        print(f"ERROR: Invalid token - {str(e)}")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error - {str(e)}")
        return None


if __name__ == "__main__":
    # Print environment diagnostics
    print("=== Environment Diagnostics ===")
    print(f"SECRET_KEY exists: {bool(get_env('SECRET_KEY'))}")
    print(f"ALGORITHM: {get_env('ALGORITHM', 'HS256')}")

    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        token = input("Enter JWT token to decode: ")

    decode_jwt(token)
