"""
Script to validate environment variables and configuration
Run before starting the application to ensure environment is properly set up
"""

import os
import sys
import dotenv
import json
from pathlib import Path


def print_section(title):
    """Print a section title with decoration"""
    print("\n" + "=" * 50)
    print(f" {title} ".center(50, "="))
    print("=" * 50 + "\n")


def check_environment_file():
    """Check if .env file exists and is properly loaded"""
    print_section("Environment File Check")

    env_paths = [
        ".env",
        "app/.env",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", ".env"),
    ]

    found = False
    for path in env_paths:
        if os.path.isfile(path):
            print(f"✅ Found .env file at: {path}")

            # Try to load it
            try:
                env_vars = dotenv.dotenv_values(path)
                print(f"   Successfully loaded {len(env_vars)} variables")
                found = True
                break
            except Exception as e:
                print(f"   ⚠️ Error loading .env file: {str(e)}")

    if not found:
        print("❌ No .env file found in standard locations!")
        print("   Please create one at app/.env or copy from .env.example")
        return False

    return True


def check_critical_variables():
    """Check critical environment variables"""
    print_section("Critical Variables Check")

    # Load environment
    dotenv.load_dotenv()

    # Critical variables that must be set
    critical_vars = {
        "APPWRITE_ENDPOINT": "Appwrite API endpoint URL",
        "APPWRITE_PROJECT_ID": "Appwrite project ID",
        "APPWRITE_API_KEY": "Appwrite API key",
        "APPWRITE_DATABASE_ID": "Appwrite database ID",
        "SECRET_KEY": "JWT secret key",
        "API_BEARER_TOKEN": "API bearer token",
    }

    all_good = True

    for var, description in critical_vars.items():
        # Check both regular and VITE_ prefixed versions
        value = os.environ.get(var)
        vite_value = os.environ.get(f"VITE_{var}")
        
        if not value and not vite_value:
            print(f"❌ Missing {var}: {description} (not found in either regular or VITE_ prefixed form)")
            all_good = False
        elif (value and ("YOUR_" in value or value == "your-secret-key" or value == "your-bearer-token")) and \
             (not vite_value or "YOUR_" in vite_value or vite_value == "your-secret-key" or vite_value == "your-bearer-token"):
            print(f"⚠️ {var} appears to be a placeholder in both regular and VITE_ prefixed form")
            all_good = False
        else:
            # Don't print full values for security
            has_regular = "✓" if value else "✗"
            has_vite = "✓" if vite_value else "✗"
            print(f"✅ {var} is set properly (Regular: {has_regular}, VITE_: {has_vite})")
    
    # Check for VITE_ prefixed variables
    print("\n--- VITE_ Prefixed Variables Check ---")
    vite_vars = [k for k in os.environ if k.startswith("VITE_")]
    print(f"Found {len(vite_vars)} VITE_ prefixed variables")
    
    # Count how many of the critical vars have VITE_ prefixes
    vite_critical_count = sum(1 for var in critical_vars if f"VITE_{var}" in vite_vars)
    if vite_critical_count < len(critical_vars):
        print(f"⚠️ Only {vite_critical_count} out of {len(critical_vars)} critical variables have VITE_ prefixed versions")
        all_good = False
    else:
        print(f"✅ All critical variables have VITE_ prefixed versions")

    return all_good


def check_api_connectivity():
    """Check connectivity to external services if possible"""
    print_section("API Connectivity Check")

    # We'll only do basic checks without actual connections
    api_url = os.environ.get("PINEAPPLE_API_BASE_URL")
    vite_api_url = os.environ.get("VITE_PINEAPPLE_API_BASE_URL")
    appwrite_url = os.environ.get("APPWRITE_ENDPOINT")
    vite_appwrite_url = os.environ.get("VITE_APPWRITE_ENDPOINT")
    
    print(f"Pineapple API URL: {api_url}")
    print(f"VITE_Pineapple API URL: {vite_api_url}")
    print(f"Appwrite Endpoint: {appwrite_url}")
    print(f"VITE_Appwrite Endpoint: {vite_appwrite_url}")

    if not api_url or "your" in api_url.lower():
        print("⚠️ Pineapple API URL may not be properly configured")
    
    if not vite_api_url or "your" in vite_api_url.lower():
        print("⚠️ VITE_PINEAPPLE_API_BASE_URL may not be properly configured")

    if not appwrite_url or "your" in appwrite_url.lower():
        print("⚠️ Appwrite Endpoint may not be properly configured")
        
    if not vite_appwrite_url or "your" in vite_appwrite_url.lower():
        print("⚠️ VITE_APPWRITE_ENDPOINT may not be properly configured")

    print("\nNote: This script doesn't test actual connectivity.")
    print("To fully validate connections, run the application and check logs.")


def check_application_requirements():
    """Check application requirements"""
    print_section("Application Requirements Check")

    # Check Python version
    python_version = sys.version_info
    print(
        f"Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}"
    )

    if python_version.major < 3 or (
        python_version.major == 3 and python_version.minor < 8
    ):
        print("❌ Python version 3.8+ is recommended")
    else:
        print("✅ Python version is adequate")

    # Check for requirements.txt
    if os.path.isfile("requirements.txt"):
        print("✅ requirements.txt found")
    else:
        print("❌ requirements.txt not found")
        
    # Check for VITE prefixed variables for frontend integration
    vite_count = len([k for k in os.environ if k.startswith("VITE_")])
    regular_count = len([k for k in os.environ if not k.startswith("VITE_") and k not in ["PATH", "PYTHONPATH", "CLASSPATH"]])
    
    print(f"\n✅ Found {vite_count} VITE_ prefixed variables out of {regular_count} regular variables")
    if vite_count < regular_count / 2:
        print("⚠️ Less than half of your variables have VITE_ prefixed versions")
        print("   Consider adding VITE_ prefixed versions for frontend compatibility")


def main():
    """Main validation function"""
    print("\n" + "=" * 80)
    print(" ENVIRONMENT VALIDATION TOOL ".center(80, "="))
    print("=" * 80 + "\n")

    print("This tool checks your environment configuration for the Pineapple Lead API")

    env_ok = check_environment_file()
    vars_ok = check_critical_variables()
    check_api_connectivity()
    check_application_requirements()

    print_section("Validation Summary")

    if env_ok and vars_ok:
        print("✅ Your environment appears to be properly configured.")
        print("   You can start the application with:")
        print("   $ uvicorn app.main:app --reload --port 8000")
    else:
        print("⚠️ Some issues were found with your environment configuration.")
        print("   Please address the warnings above before starting the application.")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
