import os
import logging
from typing import List, Any

from pydantic import (
    field_validator,
    FieldValidationInfo,
    model_validator,
)
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file variables
load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "Pineapple Integration API - V2"
    API_V1_STR: str = "/api/v1"

    # --- Required Settings (with environment variable defaults) ---
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")  # Anon or Service key

    # Fix Pineapple API URL handling - check both variable names
    PINEAPPLE_API_URL: str = os.getenv(
        "PINEAPPLE_API_URL",
        os.getenv("PINEAPPLE_API_BASE_URL", "http://gw-test.pineapple.co.za"),
    )

    # Fix Bearer token handling - check both variable names
    PINEAPPLE_API_TOKEN: str = os.getenv(
        "PINEAPPLE_API_TOKEN", os.getenv("PINEAPPLE_API_BEARER_TOKEN", "")
    )

    # --- Optional Settings with Defaults ---
    PINEAPPLE_SOURCE_NAME: str = os.getenv(
        "PINEAPPLE_SOURCE_NAME", os.getenv("PINEAPPLE_API_SOURCE", "SureStrat")
    )

    # Add endpoints
    PINEAPPLE_QUICK_QUOTE_ENDPOINT: str = os.getenv(
        "PINEAPPLE_QUICK_QUOTE_ENDPOINT", "/api/v1/quote/quick-quote"
    )
    PINEAPPLE_LEAD_TRANSFER_ENDPOINT: str = os.getenv(
        "PINEAPPLE_LEAD_TRANSFER_ENDPOINT", "/users/motor_lead"
    )

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Keep original field name to match environment variables
    BACKEND_CORS_ORIGINS: str = os.getenv("BACKEND_CORS_ORIGINS", "*")

    # Rate Limiting Defaults: Uses os.getenv within the model for flexibility
    DEFAULT_RATE_LIMIT: str = os.getenv("DEFAULT_RATE_LIMIT", "100/hour")
    LOGIN_RATE_LIMIT: str = os.getenv("LOGIN_RATE_LIMIT", "10/minute")

    # Update to Pydantic v2 style configuration
    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # Add this to ignore extra fields from environment
    }

    # Validate LOG_LEVEL using Pydantic V2 model validation
    @field_validator("LOG_LEVEL")
    @classmethod
    def check_log_level(cls, v: str) -> str:
        level = v.upper()
        if level not in logging._nameToLevel:
            raise ValueError(
                f"Invalid LOG_LEVEL: {v}. Must be one of {list(logging._nameToLevel.keys())}"
            )
        return level


# Create the settings instance (add try/except for better startup debugging)
try:
    settings = Settings()
    # Log loaded settings (avoid logging sensitive keys like SUPABASE_KEY, PINEAPPLE_API_TOKEN in production)
    # Ensure logger is configured before using it here (main.py handles this)
    temp_logger = logging.getLogger(
        __name__
    )  # Use temp logger just for this spot if needed
    temp_logger.info(
        f"Settings loaded successfully. Project: {settings.PROJECT_NAME}, "
        f"Supabase URL: {settings.SUPABASE_URL[:20] if settings.SUPABASE_URL else 'Not set'}..., "
        f"Pineapple API URL: {settings.PINEAPPLE_API_URL}, "
        f"Log Level: {settings.LOG_LEVEL}, "
        f"CORS Origins: '{settings.BACKEND_CORS_ORIGINS}'"  # Log the raw string
    )
except Exception as e:
    # Log the error during settings initialization and re-raise to stop app
    # Use standard print here as logging might not be fully set up if config fails
    print(f"CRITICAL ERROR: Failed to initialize application settings: {e}")
    # Optionally log to file here if needed before exiting
    raise  # Re-raise the exception to stop the application startup

# Basic startup validation - Make warning rather than stopping app
if not settings.PINEAPPLE_API_URL:
    temp_logger = logging.getLogger(__name__)
    temp_logger.warning("PINEAPPLE_API_URL is not set, using default URL")

if not settings.PINEAPPLE_API_TOKEN:
    temp_logger = logging.getLogger(__name__)
    temp_logger.warning(
        "PINEAPPLE_API_TOKEN/PINEAPPLE_API_BEARER_TOKEN is not set, API calls will likely fail"
    )
