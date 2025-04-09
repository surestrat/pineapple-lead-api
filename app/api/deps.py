import logging
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from supabase import Client
from gotrue.errors import AuthApiError  # Specific Supabase auth errors
from jose import JWTError, jwt  # If you were decoding manually (less needed now)

from app.db.session import get_db
from app.core.config import settings
from app.schemas import user as user_schema
from app.schemas import token as token_schema

logger = logging.getLogger(__name__)

# OAuth2 scheme pointing to your login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Client = Depends(get_db)
) -> user_schema.User:
    """
    Validates JWT token using Supabase and returns the user data.
    Handles authentication errors.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.debug("Attempting to validate token and get user from Supabase.")
        # Use Supabase client to validate the token and fetch user
        user_response = db.auth.get_user(token)

        if not user_response or not user_response.user:
            logger.warning(
                "Supabase auth.get_user returned no user for a seemingly valid token."
            )
            raise credentials_exception

        # Map Supabase user object to Pydantic V2 User schema
        # Ensure fields match your user_schema.User definition
        user_data = {
            "id": str(user_response.user.id),
            "email": user_response.user.email,
            # Add other relevant fields from user_response.user as needed:
            "aud": getattr(user_response.user, "aud", None),
            "role": getattr(user_response.user, "role", None),
            "app_metadata": getattr(user_response.user, "app_metadata", None),
            "user_metadata": getattr(user_response.user, "user_metadata", None),
            "created_at": getattr(user_response.user, "created_at", None),
            # ... etc
        }
        # Use model_validate for Pydantic V2 instantiation from dict
        user = user_schema.User.model_validate(user_data)
        # Use getattr above as Supabase object attributes might vary slightly
        logger.info(f"User {user.id} authenticated successfully.")
        return user

    except AuthApiError as e:
        # Specific handling for Supabase Auth errors (invalid token, expired, etc.)
        # Log message and status if available
        auth_error_msg = getattr(e, "message", str(e))
        auth_error_status = getattr(e, "status", "N/A")
        logger.error(
            f"Supabase Auth Error during token validation: {auth_error_msg} (Status: {auth_error_status})"
        )
        # Raise 401 Unauthorized for all auth errors for simplicity
        raise credentials_exception from e
    except Exception as e:
        # Catch any other unexpected errors during user retrieval/validation
        logger.exception("Unexpected error validating token or retrieving user.")
        raise credentials_exception from e


# Optional: Dependency for checking specific roles if using Supabase roles/claims
# async def require_role(required_role: str, current_user: user_schema.User = Depends(get_current_user)): ...
