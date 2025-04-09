"""
Rate limiting configuration for the API.
Centralized here to avoid circular imports.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# Initialize Rate Limiter
# Uses default limits from settings unless overridden per endpoint
limiter = Limiter(
    key_func=get_remote_address, default_limits=[settings.DEFAULT_RATE_LIMIT]
)
