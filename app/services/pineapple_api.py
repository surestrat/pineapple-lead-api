import os
import requests
import logging
from typing import Dict, Any
from app.core.config import settings  # Import settings directly

logger = logging.getLogger(__name__)

# Use settings directly instead of environment variables
PINEAPPLE_API_URL = settings.PINEAPPLE_API_URL
PINEAPPLE_API_BEARER_TOKEN = settings.PINEAPPLE_API_TOKEN
PINEAPPLE_SOURCE_NAME = settings.PINEAPPLE_SOURCE_NAME
PINEAPPLE_LEAD_TRANSFER_ENDPOINT = settings.PINEAPPLE_LEAD_TRANSFER_ENDPOINT
PINEAPPLE_QUICK_QUOTE_ENDPOINT = settings.PINEAPPLE_QUICK_QUOTE_ENDPOINT


def _get_headers() -> Dict[str, str]:
    """Get the authorization headers for API requests."""
    token_parts = PINEAPPLE_API_BEARER_TOKEN.split()

    # Handle both "Bearer token123" and just "token123" formats
    if len(token_parts) > 1 and token_parts[0].lower() == "bearer":
        token = PINEAPPLE_API_BEARER_TOKEN
    else:
        token = f"Bearer {PINEAPPLE_API_BEARER_TOKEN}"

    return {
        "Authorization": token,
        "Content-Type": "application/json",
    }


def get_quick_quote(quote_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Submit a quick quote request to get insurance premium estimate.

    Args:
        quote_data: Vehicle and driver information for quote calculation

    Returns:
        API response with premium and excess information
    """
    # Ensure source is set
    if "source" not in quote_data:
        quote_data["source"] = PINEAPPLE_SOURCE_NAME

    url = f"{PINEAPPLE_API_URL}{PINEAPPLE_QUICK_QUOTE_ENDPOINT}"

    logger.debug(f"Quick quote data: {quote_data}")

    try:
        logger.info(f"Sending quick quote request to Pineapple API: {url}")
        headers = _get_headers()
        logger.debug(f"Using headers: {headers}")

        response = requests.post(url, headers=headers, json=quote_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting quick quote from Pineapple: {str(e)}")
        if hasattr(e, "response") and e.response:
            logger.error(f"Response: {e.response.text}")
        raise


def transfer_lead(lead_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transfer a lead to Pineapple's system.

    Args:
        lead_data: Lead information containing contact details

    Returns:
        API response with success status and redirect URL
    """
    # Ensure source is set
    if "source" not in lead_data:
        lead_data["source"] = PINEAPPLE_SOURCE_NAME

    url = f"{PINEAPPLE_API_URL}{PINEAPPLE_LEAD_TRANSFER_ENDPOINT}"

    logger.debug(f"Lead transfer data: {lead_data}")

    try:
        logger.info(f"Sending lead transfer request to Pineapple API: {url}")
        headers = _get_headers()
        logger.debug(f"Using headers: {headers}")

        response = requests.post(url, headers=headers, json=lead_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error transferring lead to Pineapple: {str(e)}")
        if hasattr(e, "response") and e.response:
            logger.error(f"Response: {e.response.text}")
        raise


# Add PineappleAPIService class that was referenced but missing
class PineappleAPIService:
    """Service class for Pineapple API interactions."""

    def __init__(self):
        self.base_url = PINEAPPLE_API_URL
        self.headers = _get_headers()
        self.source = PINEAPPLE_SOURCE_NAME

    def submit_quick_quote(self, quote_data: Dict[str, Any]) -> Dict[str, Any]:
        """Wrapper for quick quote functionality."""
        return get_quick_quote(quote_data)

    def transfer_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Wrapper for lead transfer functionality."""
        return transfer_lead(lead_data)
