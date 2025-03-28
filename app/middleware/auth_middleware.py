from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.config.settings import settings
from app.utils.logger import logger
import jwt


class BearerTokenMiddleware(BaseHTTPMiddleware):
    """
    Middleware that validates bearer tokens for protected endpoints.
    This middleware is now configured to only log information about requests
    but not enforce authentication, which is handled directly by the route handlers.

    Attributes:
        None
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        logger.debug(f"Processing request to path: {path}")

        # If the path is a protected endpoint, we'll log information but let the route handler do the auth
        if path in settings.protected_endpoints:
            logger.debug(
                f"Path {path} is protected, authentication will be checked by route handler"
            )
            authorization = request.headers.get("Authorization")

            if not authorization or not authorization.startswith("Bearer "):
                logger.debug(
                    f"Request to {path} has no Bearer token - auth will be handled by route"
                )
            else:
                logger.debug(
                    f"Request to {path} has a Bearer token - auth will be handled by route"
                )

        response = await call_next(request)
        return response
