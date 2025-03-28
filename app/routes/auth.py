from fastapi import APIRouter, Request
from app.schemas.auth_schemas import Token, User
from app.services.auth_services import authenticate_user
from app.utils.logger import logger

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(user: User, request: Request):
    """Get an access token with username and password."""
    logger.debug("==== LOGIN REQUEST ====")
    client_ip = request.client.host if request.client else "Unknown"
    logger.debug(f"Client IP: {client_ip}")
    logger.debug(f"Headers: {dict(request.headers)}")
    logger.debug(f"Login request for user: {user.username}")

    token = await authenticate_user(user)

    # Add debug information about the token
    logger.debug(f"Generated token with length: {len(token.access_token)}")
    logger.debug(f"Token type: {token.token_type}")

    logger.debug("Login successful, returning token")
    return token
