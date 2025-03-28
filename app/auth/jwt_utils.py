import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Security, Request
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordBearer,
)
from app.config.settings import settings
from app.utils.logger import logger

# Update security configuration
security = HTTPBearer(
    scheme_name="Bearer", description="Enter the Bearer token", auto_error=True
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token from the provided data.
    This function takes a dictionary of data to encode in the token and an optional expiration
    time delta. If no expiration is provided, the token will expire in 15 minutes by default.
    Args:
        data (dict): The payload data to encode in the JWT.
        expires_delta (Optional[timedelta], optional): The time delta after which the token expires.
            Defaults to None, which results in a 15-minute expiration.
    Returns:
        str: The encoded JWT access token string.
    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
        >>> token = create_access_token({"sub": "user@example.com"}, timedelta(hours=1))
    """
    logger.debug(f"Creating access token with payload: {data}")
    logger.debug(f"Token expires_delta: {expires_delta}")
    logger.debug(f"Using SECRET_KEY length: {len(settings.secret_key)}")
    logger.debug(f"Using algorithm: {settings.algorithm}")

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    logger.debug(f"Token will expire at: {expire}")

    try:
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        logger.debug(f"Token created successfully. Length: {len(encoded_jwt)}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating JWT token: {str(e)}")
        raise


def decode_access_token(token: str) -> dict:
    """
    Decode a JWT access token and return its payload.
    Args:
        token (str): The JWT token to decode.
    Returns:
        dict: The decoded payload from the token.
    Raises:
        HTTPException: If the token has expired (status_code=401).
        HTTPException: If the token is invalid (status_code=401).
    """
    logger.debug(f"Decoding token with length: {len(token)}")

    try:
        # First try to get unverified header for debugging
        try:
            header = jwt.get_unverified_header(token)
            logger.debug(f"Token header: {header}")
        except Exception as e:
            logger.warning(f"Could not parse token header: {str(e)}")

        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        logger.debug(f"Token decoded successfully. Payload: {payload}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Token validation error: {str(e)}")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """Retrieves the current user from the JWT token."""
    logger.debug("Attempting to get current user from token")

    if not credentials:
        logger.warning("No credentials provided")
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.debug(f"Credentials scheme: {credentials.scheme}")
    logger.debug(f"Token length: {len(credentials.credentials)}")

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        logger.debug(f"User authenticated. Payload: {payload}")
        return payload
    except HTTPException as e:
        logger.warning(f"Authentication failed: {e.detail}")
        raise


# Add helper function to extract token from request
def get_token_from_request(request: Request) -> Optional[str]:
    """
    Extract bearer token from a request object.
    Args:
        request (Request): The FastAPI request object
    Returns:
        Optional[str]: The token string or None if not found
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    return auth_header.split(" ")[1]
