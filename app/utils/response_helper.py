"""
Helper utilities for formatting responses in a consistent way.
"""

from fastapi import Request
from app.schemas.lead_schemas import LeadTransferResponse


def enhance_response(
    response: LeadTransferResponse, request: Request
) -> LeadTransferResponse:
    """
    Enhance a response object with additional information like absolute URLs.

    Args:
        response: The response object to enhance
        request: The FastAPI request object (for base URL)

    Returns:
        Enhanced response object
    """
    # Make redirect URLs absolute if they're relative
    if hasattr(response, "data") and hasattr(response.data, "redirect_url"):
        if response.data.redirect_url.startswith("/"):
            base_url = str(request.base_url).rstrip("/")
            response.data.redirect_url = f"{base_url}{response.data.redirect_url}"

    return response


def format_pineapple_response(pineapple_response: dict, local_id: str) -> dict:
    """
    Format a Pineapple API response into a standardized format.

    Args:
        pineapple_response: Raw response from Pineapple API
        local_id: Local document ID to include in the response

    Returns:
        Standardized response dictionary
    """
    result = {
        "success": True,
        "data": {
            "uuid": local_id,
            "pineapple_uuid": None,
            "redirect_url": f"/leads/{local_id}",
            "pineapple_redirect_url": None,
            "source": "local",
        },
    }

    # Extract data from Pineapple response if available
    if isinstance(pineapple_response, dict):
        # Check if success status is present
        if "success" in pineapple_response:
            result["success"] = pineapple_response["success"]

        # Extract data if present
        pineapple_data = pineapple_response.get("data", {})

        # Get Pineapple UUID if available
        if isinstance(pineapple_data, dict) and "uuid" in pineapple_data:
            result["data"]["pineapple_uuid"] = pineapple_data["uuid"]

        # Get Pineapple redirect URL if available
        if isinstance(pineapple_data, dict) and "redirect_url" in pineapple_data:
            result["data"]["pineapple_redirect_url"] = pineapple_data["redirect_url"]
            # If a Pineapple redirect URL is available, use it as the primary redirect
            result["data"]["redirect_url"] = pineapple_data["redirect_url"]
            result["data"]["source"] = "pineapple"

    return result
