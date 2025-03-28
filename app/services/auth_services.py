from fastapi import HTTPException
from app.auth.jwt_utils import create_access_token
from datetime import timedelta
from app.schemas.auth_schemas import Token, User
from app.config.settings import settings
from app.utils.logger import logger


async def authenticate_user(user: User) -> Token:
    """Authenticate user and return access token"""
    logger.debug("==== AUTHENTICATION ATTEMPT ====")
    logger.debug(f"Received username: '{user.username}'")
    logger.debug(f"Password length: {len(user.password) if user.password else 0}")

    # Log environment variables for debugging
    logger.debug(f"Settings TEST_USERNAME: '{settings.test_username}'")
    logger.debug(f"Settings TEST_PASSWORD: '{settings.test_password}'")

    # Check for empty credentials
    if not user.username or not user.password:
        logger.warning("Empty username or password provided")
        raise HTTPException(status_code=400, detail="Username and password required")

    # Check credentials match
    username_match = user.username == settings.test_username
    password_match = user.password == settings.test_password

    logger.debug(f"Username match: {username_match}")
    logger.debug(f"Password match: {password_match}")

    if username_match and password_match:
        logger.info(f"Authentication successful for user: {user.username}")
        # Create token with 30-minute expiration
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=timedelta(minutes=30)
        )
        logger.debug(f"Token created successfully. Token length: {len(access_token)}")
        return Token(access_token=access_token)

    # Log which credential failed
    if not username_match:
        logger.warning(
            f"Username mismatch: Expected '{settings.test_username}', got '{user.username}'"
        )
    if not password_match:
        logger.warning("Password mismatch")

    logger.warning(f"Authentication failed for user: {user.username}")
    raise HTTPException(status_code=401, detail="Invalid credentials")
