from fastapi import APIRouter, HTTPException, Depends, Request
from app.schemas.auth_schemas import User, Token
from app.services.auth_services import authenticate_user
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from app.config.settings import settings

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/token", response_model=Token)
@limiter.limit(f"{settings.rate_limit}/minute")
async def login_for_access_token(request: Request, user: User):
    """Endpoint to authenticate a user and return an access token.
    This function authenticates a user and returns a JWT access token if the
    credentials are valid.
    Args:
        request (Request): The incoming HTTP request.
        user (User): The user credentials provided for authentication.
    Returns:
        dict: A dictionary containing the access token and token type if authentication
            is successful. The token is a JWT with an expiration time.
    Raises:
        HTTPException: If authentication fails due to invalid credentials.
    """

    return await authenticate_user(user)
