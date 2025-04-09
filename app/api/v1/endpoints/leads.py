import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from supabase import Client
from gotrue.errors import AuthApiError

from app.schemas import token as token_schema
from app.schemas import user as user_schema
from app.api import deps
from app.main import limiter
from app.core.config import settings
from app.services.pineapple_api import transfer_lead
from app.models.pineapple import LeadTransferRequest, LeadTransferResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/login",
    response_model=token_schema.Token,
    summary="Login for Access Token",
    description="Authenticate using email and password to receive JWT access and refresh tokens.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Incorrect email or password"},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Rate limit exceeded"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)
@limiter.limit(settings.LOGIN_RATE_LIMIT)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    supabase_client: Client = Depends(deps.get_db),
):
    """
    OAuth2 compatible token login using Supabase email/password sign-in.
    Rate limited.
    """
    email = form_data.username
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
        logger.warning(
            f"Supabase Sign-in Error for email {email}: {auth_error_msg} (Status: {auth_error_status})"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
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
    current_user: user_schema.User = Depends(deps.get_current_user),
):
    """
    Test endpoint requiring a valid bearer token. Returns user information if the token is valid.
    Useful for frontend checks to see if the user is still logged in.
    """
    logger.info(f"Token test successful for user ID: {current_user.id}")
    return current_user


@router.post("/transfer", response_model=LeadTransferResponse)
async def create_lead_transfer(
    lead_request: LeadTransferRequest,
    current_user: user_schema.User = Depends(deps.get_current_user),
    db: Client = Depends(deps.get_db),
):
    """
    Transfer a lead to Pineapple's system.

    This endpoint forwards lead information to Pineapple and returns a success status and redirect URL.
    """
    try:
        response = transfer_lead(lead_request.model_dump())
        logger.info(f"Lead transfer successful for user {current_user.id}")
        return response
    except Exception as e:
        logger.error(f"Error transferring lead: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transfer lead: {str(e)}",
        )


# Optional: Add token refresh endpoint if manual refresh is needed by clients
# @router.post("/refresh", response_model=token_schema.Token)
# async def refresh_access_token(refresh_request: RefreshTokenSchema, ...)
