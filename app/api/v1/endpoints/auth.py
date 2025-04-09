import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request  # Added Request
from fastapi.security import OAuth2PasswordRequestForm
from supabase import Client
from gotrue.errors import AuthApiError

from app.schemas import token as token_schema
from app.schemas import user as user_schema
from app.api import deps
from app.main import limiter  # Import limiter instance
from app.core.config import settings  # Import settings for rate limit config

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/login",
    response_model=token_schema.Token,
    summary="Login for Access Token",
    description="Authenticate using email and password to receive JWT access and refresh tokens.",
    responses={  # Define potential error responses
        status.HTTP_401_UNAUTHORIZED: {"description": "Incorrect email or password"},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Rate limit exceeded"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)
@limiter.limit(settings.LOGIN_RATE_LIMIT)  # Apply specific login rate limit
async def login_for_access_token(
    request: Request,  # Needed for limiter
    form_data: OAuth2PasswordRequestForm = Depends(),
    supabase_client: Client = Depends(deps.get_db),
):
    """
    OAuth2 compatible token login using Supabase email/password sign-in.
    Rate limited.
    """
    email = form_data.username  # form_data uses 'username' field for email
    password = form_data.password
    logger.info(f"Login attempt for email: {email}")
    try:
        auth_response = supabase_client.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        if (
            not auth_response
            or not auth_response.session
            or not auth_response.session.access_token
        ):
            logger.error(
                f"Unexpected Supabase sign-in response format for email {email}: {auth_response}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed due to unexpected response format from auth provider.",
            )

        logger.info(f"Successful login for email: {email}")
        # Map response to Pydantic Token model (V2 uses model_validate)
        token_data = {
            "access_token": auth_response.session.access_token,
            "token_type": getattr(auth_response.session, "token_type", "bearer"),
            "refresh_token": getattr(auth_response.session, "refresh_token", None),
            "expires_in": getattr(auth_response.session, "expires_in", None),
        }
        return token_schema.Token.model_validate(token_data)

    except AuthApiError as e:
        auth_error_msg = getattr(e, "message", str(e))
        auth_error_status = getattr(e, "status", "N/A")
        # Log specific Supabase error
        logger.warning(
            f"Supabase Sign-in Error for email {email}: {auth_error_msg} (Status: {auth_error_status})"
        )
        # Return 401 for invalid credentials
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",  # Keep generic message for security
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.exception(f"Unexpected error during login for email {email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred during login.",
        )


@router.post(
    "/test-token", response_model=user_schema.User, summary="Test Authentication Token"
)
async def test_token(
    # This endpoint implicitly tests the token via the dependency
    current_user: user_schema.User = Depends(deps.get_current_user),
):
    """
    Test endpoint requiring a valid bearer token. Returns user information if the token is valid.
    Useful for frontend checks to see if the user is still logged in.
    """
    logger.info(f"Token test successful for user ID: {current_user.id}")
    return current_user


# Optional: Add token refresh endpoint if manual refresh is needed by clients
# @router.post("/refresh", response_model=token_schema.Token)
# async def refresh_access_token(refresh_request: RefreshTokenSchema, ...)
