"""
Utility for diagnosing environment variable issues.
Run this script directly to check environment variable loading.
"""

import os
import sys
from dotenv import load_dotenv
from pathlib import Path


def check_env_files():
    """Check for .env files in various locations"""
    print("=== Checking for .env files ===")

    # Current directory
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")

    # Possible locations
    locations = [
        os.path.join(cwd, ".env"),
        os.path.join(cwd, "app", ".env"),
        os.path.join(Path(__file__).parent.parent.parent, ".env"),
        os.path.join(Path(__file__).parent.parent, ".env"),
    ]

    found = False
    for loc in locations:
        if os.path.isfile(loc):
            print(f"✅ Found .env file at: {loc}")

            # Check file permissions
            try:
                with open(loc, "r") as f:
                    content = f.read()
                    lines = content.count("\n") + 1
                    print(f"   File readable: Yes ({lines} lines)")
                    
                    # Count VITE_ prefixed vars
                    vite_count = sum(1 for line in content.split('\n') if line.strip().startswith('VITE_'))
                    print(f"   VITE_ prefixed variables: {vite_count}")
            except Exception as e:
                print(f"   ❌ File read error: {str(e)}")

            found = True
        else:
            print(f"❌ No .env file at: {loc}")

    if not found:
        print("⚠️ WARNING: No .env files found in standard locations!")

    return found


def load_and_check_variables():
    """Load .env and check critical variables"""
    print("\n=== Loading environment variables ===")

    # Try to load from the most likely location
    env_path = os.path.join(os.getcwd(), "app", ".env")
    if os.path.isfile(env_path):
        load_dotenv(env_path)
        print(f"Loaded variables from {env_path}")
    else:
        print("No .env file found to load")

    # Check critical variables
    critical_vars = [
        "SECRET_KEY", 
        "ALGORITHM",
        "APPWRITE_ENDPOINT",
        "APPWRITE_PROJECT_ID", 
        "APPWRITE_API_KEY",
        "API_BEARER_TOKEN",
        "TEST_USERNAME",
        "TEST_PASSWORD",
    ]

    print("\n=== Critical Environment Variables ===")
    all_good = True
    for var in critical_vars:
        # Check regular variable
        value = os.environ.get(var)

        # Check with VITE_ prefix if not found
        vite_value = os.environ.get(f"VITE_{var}")

        if value is not None:
            print(f"{var}: ✅ Present (length: {len(value)})")
        elif vite_value is not None:
            print(f"{var}: ✅ Present with VITE_ prefix (length: {len(vite_value)})")
        else:
            print(f"{var}: ❌ Missing")
            all_good = False
            
        # Check if there's a VITE_ version regardless of regular version
        if vite_value is None:
            print(f"   ⚠️ No VITE_ prefixed version found for {var}")
            all_good = False

    # Check for any VITE_ prefixed variables
    print("\n=== VITE_ Prefixed Variables ===")
    vite_vars = [k for k in os.environ if k.startswith("VITE_")]
    if vite_vars:
        for var in vite_vars:
            if var == "VITE_SECRET_KEY" or var == "VITE_API_BEARER_TOKEN":
                print(f"Found: {var} (length: {len(os.environ[var])})")
            else:
                print(f"Found: {var}")
    else:
        print("No VITE_ prefixed variables found")
        all_good = False
        
    # Compare counts
    regular_vars = [k for k in os.environ if any(k.startswith(prefix) for prefix in ["API_", "APP", "SECRET", "PIN", "TEST_"]) and not k.startswith("VITE_")]
    vite_count = len(vite_vars)
    regular_count = len(regular_vars)
    
    print(f"\nFound {regular_count} regular variables and {vite_count} VITE_ prefixed variables")
    if vite_count < regular_count:
        print(f"⚠️ Missing VITE_ prefixed versions for {regular_count - vite_count} variables")
        all_good = False
    
    if all_good:
        print("\n✅ All critical variables have both regular and VITE_ prefixed versions!")
    else:
        print("\n⚠️ Some variables are missing their VITE_ prefixed versions")


if __name__ == "__main__":
    print("Environment Variable Diagnosis Tool")
    print("==================================")

    check_env_files()
    load_and_check_variables()

    print(
        "\nDiagnosis complete. If issues persist, ensure your .env file is properly formatted and contains the required variables."
    )
