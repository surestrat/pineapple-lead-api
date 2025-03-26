import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config.settings import settings

security = HTTPBearer()


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

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


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

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """Retrieves the current user from the JWT token."""
    token = credentials.credentials
    payload = decode_access_token(token)
    return payload
