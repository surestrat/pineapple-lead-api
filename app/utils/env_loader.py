"""
Utility for consistent environment variable loading across the application.
This module ensures that all parts of the application load environment variables
in a standardized way, supporting both regular variables and VITE_ prefixed ones.
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path


def load_env_files(verbose=False):
    """
    Load environment variables from .env files with proper error handling

    Args:
        verbose (bool): Whether to print debug information

    Returns:
        bool: True if an env file was loaded, False otherwise
    """
    # Try standard locations
    locations = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.getcwd(), "app", ".env"),
        os.path.join(Path(__file__).parent.parent.parent, ".env"),
        os.path.join(Path(__file__).parent.parent, ".env"),
    ]

    for loc in locations:
        if os.path.isfile(loc):
            if verbose:
                print(f"Loading environment from: {loc}")
            load_dotenv(loc)
            return True

    if verbose:
        print(
            "No .env file found in standard locations. Using environment variables only."
        )
    return False


def get_env(key, default=None, verbose=False):
    """
    Get an environment variable with support for VITE_ prefix

    Args:
        key (str): The environment variable name to look for
        default: Default value to return if not found
        verbose (bool): Whether to print debug information

    Returns:
        str: The environment variable value or default
    """
    # Try regular key
    value = os.environ.get(key)
    if value is not None:
        return value

    # Try with VITE_ prefix
    vite_key = f"VITE_{key}"
    value = os.environ.get(vite_key)
    if value is not None:
        if verbose:
            print(f"Using VITE_ prefixed value for {key}")
        return value

    # Return default if neither exists
    return default


def print_env_diagnostics(variables=None):
    """
    Print diagnostic information about environment variables

    Args:
        variables (list): List of variable names to check, or None for defaults
    """
    if variables is None:
        variables = [
            "SECRET_KEY",
            "ALGORITHM",
            "APPWRITE_ENDPOINT",
            "APPWRITE_PROJECT_ID",
            "APPWRITE_API_KEY",
            "API_BEARER_TOKEN",
            "TEST_USERNAME",
            "TEST_PASSWORD",
        ]

    print("\n=== Environment Variables Diagnostics ===")
    for var in variables:
        # Check regular variable
        value = get_env(var)

        if value is not None:
            # Mask sensitive values
            if any(
                sensitive in var.upper()
                for sensitive in ["KEY", "SECRET", "TOKEN", "PASSWORD"]
            ):
                print(f"{var}: ✓ Present (length: {len(value)})")
            else:
                print(f"{var}: ✓ Present (value: {value})")
        else:
            print(f"{var}: ✗ Missing")

    # Check for any VITE_ prefixed variables
    vite_vars = [k for k in os.environ if k.startswith("VITE_")]
    if vite_vars:
        print("\nFound VITE_ prefixed variables:")
        for var in vite_vars:
            print(f"  - {var}")


# Auto-load environment variables when this module is imported
load_env_files()

if __name__ == "__main__":
    print("Environment Variable Loader")
    print("==========================")

    load_env_files(verbose=True)
    print_env_diagnostics()
