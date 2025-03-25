from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator, Field
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings managed by Pydantic."""

    # API Information
    PROJECT_NAME: str = "FastAPI Lead and Quote API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = "your_secret_key"

    # Debug mode
    DEBUG: bool = False

    # Database - explicitly use aiosqlite as the default
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    # CORS - use a normal field name with an alias
    allowed_hosts: str = Field(default="localhost,127.0.0.1", alias="ALLOWED_HOSTS")

    # Add PORT to accepted fields
    port: int = Field(default=8000, alias="PORT")

    # Pineapple API settings
    PINEAPPLE_API_TOKEN: str = Field(
        default="your_pineapple_api_token", alias="PINEAPPLE_API_TOKEN"
    )

    # Model configuration
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",  # Allow extra fields in environment without error
        "populate_by_name": True,  # Allow population by field name and alias
    }

    def get_async_database_url(self) -> str:
        """Return database URL configured for async drivers."""
        url = self.DATABASE_URL

        # Handle SQLite
        if url.startswith("sqlite:"):
            if not url.startswith("sqlite+aiosqlite:"):
                url = url.replace("sqlite:", "sqlite+aiosqlite:", 1)

        # Handle PostgreSQL
        elif url.startswith("postgresql:"):
            if not url.startswith("postgresql+asyncpg:"):
                url = url.replace("postgresql:", "postgresql+asyncpg:", 1)

        return url

    def get_allowed_hosts(self) -> List[str]:
        """Convert comma-separated ALLOWED_HOSTS string to list."""
        if isinstance(self.allowed_hosts, str):
            return [
                host.strip() for host in self.allowed_hosts.split(",") if host.strip()
            ]
        return ["localhost", "127.0.0.1"]  # Default fallback


# Create a global settings object
settings = Settings()
