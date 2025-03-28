"""
Utility for direct interactions with the Pineapple API.
This provides a standardized way to make requests to Pineapple API endpoints.
"""

import httpx
import os
from typing import Dict, Any, Optional
from app.config.settings import settings
from app.utils.logger import logger
from app.utils.json_utils import to_json


class PineappleClient:
    """
    Client for interacting with the Pineapple API.
    """

    @staticmethod
    def format_token(api_token: str, secret: str) -> str:
        """
        Format the API token correctly for Pineapple API.

        Args:
            api_token: The API token
            secret: The secret key

        Returns:
            Properly formatted bearer token
        """
        # Check if token already has KEY= and SECRET= format
        if "KEY=" in api_token and "SECRET=" in api_token:
            return f"Bearer {api_token}"

        # Format with separate KEY and SECRET
        return f"Bearer KEY={api_token} SECRET={secret}"

    @staticmethod
    async def send_request(
        endpoint: str, data: Dict[str, Any], method: str = "POST", timeout: float = 30.0
    ) -> Dict[str, Any]:
        """
        Send a request to the Pineapple API.

        Args:
            endpoint: API endpoint (without base URL)
            data: Request data
            method: HTTP method
            timeout: Request timeout in seconds

        Returns:
            Response data from Pineapple API

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        # Get API credentials
        api_token = settings.api_bearer_token
        secret = os.environ.get("SECRET", "")

        if not api_token:
            raise ValueError("API_BEARER_TOKEN not configured")

        # Format token
        token = PineappleClient.format_token(api_token, secret)

        # Set up headers
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Build URL
        url = f"{settings.pineapple_api_base_url}{endpoint}"

        # Serialize data with proper date handling
        json_data = to_json(data)

        logger.debug(f"Sending {method} request to Pineapple API: {url}")
        logger.debug(f"Data: {json_data[:200]}...")

        # Send request
        async with httpx.AsyncClient(timeout=timeout) as client:
            if method.upper() == "POST":
                response = await client.post(url, content=json_data, headers=headers)
            elif method.upper() == "GET":
                response = await client.get(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Check for errors
            response.raise_for_status()

            # Parse response
            response_data = response.json()
            logger.debug(f"Pineapple API response: {response_data}")

            return response_data
