import logging
from rich.logging import RichHandler
import fastapi
import httpx
import sys

# Import settings carefully, ensure it's loaded when needed
# from app.core.config import settings


def setup_logging(log_level_str: str = "INFO"):  # Pass level from main.py
    """Configures logging using Rich Handler."""
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    # Base configuration using RichHandler
    logging.basicConfig(
        level=log_level,
        format="%(message)s",  # RichHandler manages format based on context
        datefmt="[%X]",  # Time format for logs
        handlers=[
            RichHandler(
                rich_tracebacks=True,
                tracebacks_word_wrap=False,
                tracebacks_suppress=[fastapi, httpx],  # Optional: Clean up tracebacks
                markup=True,  # Enable Rich markup
            )
        ],
        force=True,  # Override any existing handlers (useful if re-running setup)
    )

    # Silence overly verbose libraries if necessary
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    # logging.getLogger("httpx").setLevel(logging.WARNING) # Uncomment if httpx is too noisy

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with handler: RichHandler, level: {log_level_str}")


# Call setup_logging() ONCE at application startup (e.g., in main.py lifespan start), passing settings.LOG_LEVEL
