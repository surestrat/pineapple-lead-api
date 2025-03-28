import os
from dotenv import load_dotenv
import logging
import sys

# Create a basic console logger for init messages
init_logger = logging.getLogger("settings_init")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
init_logger.addHandler(handler)
init_logger.setLevel(logging.INFO)


# Load environment variables properly
def load_env_files():
    """Load environment variables from .env files with proper error handling"""
    # Try standard locations
    locations = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.getcwd(), "app", ".env"),
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
        ),
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "app", ".env"
        ),
    ]

    for loc in locations:
        if os.path.isfile(loc):
            init_logger.info(f"Loading environment from: {loc}")
            load_dotenv(loc)
            return True

    init_logger.warning(
        "No .env file found in standard locations. Using environment variables only."
    )
    return False


# Load environment
env_loaded = load_env_files()

# Print debug info about environment variables
init_logger.info("Environment variables processing started")
vite_vars = [k for k in os.environ if k.startswith("VITE_")]
regular_vars = [
    k
    for k in os.environ
    if k.startswith(("TEST_", "API_", "APP", "SECRET", "PIN"))
    and not k.startswith("VITE_")
]

# Log the loaded environment variables
init_logger.info(f"Found {len(regular_vars)} regular variables")
init_logger.info(f"Found {len(vite_vars)} VITE_ prefixed variables")

for key in vite_vars:
    init_logger.debug(f"Found VITE_ prefixed variable: {key}")


# Helper function to get environment variables with fallbacks and VITE_ prefix support
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
        init_logger.debug(f"Using VITE_ prefixed value for {key}: {vite_key}")
        return value

    # Return default if neither exists
    return default


# Helper function to format Pineapple API bearer token
def format_pineapple_bearer_token(api_token, secret=None):
    """
    Format the Pineapple API bearer token in the correct format: KEY=xxx SECRET=yyy

    Args:
        api_token (str): The API token value
        secret (str, optional): The secret value if separate

    Returns:
        str: Properly formatted bearer token for Pineapple API
    """
    # If token already contains KEY= and SECRET=, return as is
    if api_token and "KEY=" in api_token and "SECRET=" in api_token:
        return api_token

    # If we have both token and secret, format them
    if api_token and secret:
        return f"KEY={api_token} SECRET={secret}"

    # If we only have token but no secret, see if token contains both parts
    if api_token and not secret:
        # Try to get SECRET from environment
        env_secret = get_env("SECRET", "")
        if env_secret:
            return f"KEY={api_token} SECRET={env_secret}"

    # Return original token as fallback
    return api_token


class Settings:
    """Configuration settings for the application."""

    # Core settings
    secret_key: str = get_env("SECRET_KEY", "your-secret-key")
    algorithm: str = get_env("ALGORITHM", "HS256")

    # Appwrite settings
    appwrite_endpoint: str = get_env("APPWRITE_ENDPOINT", "YOUR_APPWRITE_ENDPOINT")
    appwrite_project_id: str = get_env(
        "APPWRITE_PROJECT_ID", "YOUR_APPWRITE_PROJECT_ID"
    )
    appwrite_api_key: str = get_env("APPWRITE_API_KEY", "YOUR_APPWRITE_API_KEY")
    appwrite_database_id: str = get_env("APPWRITE_DATABASE_ID", "YOUR_DATABASE_ID")
    appwrite_leads_collection_id: str = get_env("APPWRITE_LEADS_COLLECTION_ID", "leads")
    appwrite_quotes_collection_id: str = get_env(
        "APPWRITE_QUOTES_COLLECTION_ID", "quotes"
    )

    # API settings
    rate_limit: int = int(get_env("RATE_LIMIT", 100))
    log_level: str = get_env("LOG_LEVEL", "INFO")

    # API token - check multiple possible keys and format
    api_bearer_token_raw: str = get_env(
        "API_BEARER_TOKEN", get_env("API_BEARER_TOKEN_KEY", "your-bearer-token")
    )
    secret: str = get_env("SECRET", "")

    # Format the bearer token correctly for Pineapple API
    api_bearer_token: str = format_pineapple_bearer_token(api_bearer_token_raw, secret)

    # Routes
    protected_endpoints: list = get_env(
        "PROTECTED_ENDPOINTS", "/api/v1/leads,/api/v1/quotes"
    ).split(",")

    # External API
    pineapple_api_base_url: str = get_env(
        "PINEAPPLE_API_BASE_URL", "http://gw-test.pineapple.co.za"
    )
    pineapple_lead_endpoint: str = get_env(
        "PINEAPPLE_LEAD_ENDPOINT", "/users/motor_lead"
    )
    pineapple_quote_endpoint: str = get_env(
        "PINEAPPLE_QUOTE_ENDPOINT", "/api/v1/quote/quick-quote"
    )

    # Test credentials - check both normal and VITE_ prefixed versions
    test_username: str = get_env("TEST_USERNAME", "test")
    test_password: str = get_env("TEST_PASSWORD", "test")

    def validate_api_token(self):
        """Validate that API token is correctly formatted and log warnings if not"""
        if not self.api_bearer_token:
            init_logger.error("API_BEARER_TOKEN is missing! API calls will fail.")
            return False

        if "KEY=" not in self.api_bearer_token:
            init_logger.warning(
                "API token does not include KEY= prefix, which may be required"
            )

        if "SECRET=" not in self.api_bearer_token:
            init_logger.warning(
                "API token does not include SECRET= part, which may be required"
            )

        return "KEY=" in self.api_bearer_token and "SECRET=" in self.api_bearer_token

    def __init__(self):
        # Log critical settings during initialization
        init_logger.info(f"Auth settings loaded:")
        init_logger.info(f"TEST_USERNAME: {self.test_username}")
        init_logger.info(f"TEST_PASSWORD exists: {bool(self.test_password)}")
        init_logger.info(f"SECRET_KEY exists: {bool(self.secret_key)}")
        init_logger.info(f"ALGORITHM: {self.algorithm}")

        # Log bearer token format information (without revealing the full token)
        token_format = (
            "KEY=xxx SECRET=xxx format"
            if "KEY=" in self.api_bearer_token and "SECRET=" in self.api_bearer_token
            else (
                "KEY=xxx format (missing SECRET)"
                if "KEY=" in self.api_bearer_token
                else "plain format (may not work with Pineapple API)"
            )
        )
        init_logger.info(
            f"API_BEARER_TOKEN exists: {bool(self.api_bearer_token)} ({token_format})"
        )

        # Validate API token format
        self.validate_api_token()

        # Log Appwrite settings
        init_logger.info(f"APPWRITE_ENDPOINT: {self.appwrite_endpoint}")
        init_logger.info(
            f"APPWRITE_PROJECT_ID: {self.appwrite_project_id[:5]}... (truncated)"
        )
        init_logger.info(f"APPWRITE_DATABASE_ID: {self.appwrite_database_id}")

        # Log VITE-prefixed variables availability
        for setting_name in dir(self):
            # Skip private attributes and methods
            if setting_name.startswith("_") or callable(getattr(self, setting_name)):
                continue

            # Check if there's a VITE_ version
            vite_var_name = f"VITE_{setting_name.upper()}"
            if os.environ.get(vite_var_name):
                init_logger.debug(
                    f"Found VITE version for {setting_name}: {vite_var_name}"
                )


# Create settings instance
settings = Settings()

# Configure the logger now that settings are loaded
# Import here after Settings is initialized to avoid circular imports
from app.utils.logger import configure_logger

configure_logger(settings.log_level)
