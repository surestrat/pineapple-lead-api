from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.settings import settings
from app.utils.logger import logger


class BearerTokenMiddleware(BaseHTTPMiddleware):
    """
    Middleware that validates bearer tokens for protected endpoints.
    This middleware intercepts incoming requests and checks if they include a valid
    bearer token in the Authorization header when accessing protected endpoints
    defined in the application settings.
    Attributes:
        None
    Raises:
        HTTPException: With status code 401 if the bearer token is missing, invalid,
            or doesn't match the configured API token.
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in settings.protected_endpoints:
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                logger.warning(f"Missing or invalid bearer token for endpoint: {path}")
                raise HTTPException(
                    status_code=401, detail="Missing or invalid bearer token"
                )

            token = authorization.split(" ")[1]
            if token != settings.api_bearer_token:
                logger.warning(f"Invalid bearer token provided for endpoint: {path}")
                raise HTTPException(status_code=401, detail="Invalid bearer token")

        response = await call_next(request)
        return response
