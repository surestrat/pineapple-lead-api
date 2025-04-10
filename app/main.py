import logging
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, Request, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse


from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware


from app.core.rate_limiter import limiter

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging


setup_logging(log_level_str=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


pineapple_router: APIRouter | None = None
HAS_PINEAPPLE_ROUTES = False


try:
    from app.api.routes.pineapple_routes import router as pineapple_router

    HAS_PINEAPPLE_ROUTES = pineapple_router is not None
    logger.info("Successfully imported Pineapple routes")
except ImportError as e:
    logger.warning(
        f"Pineapple routes module not found, will not include these endpoints: {e}"
    )
    HAS_PINEAPPLE_ROUTES = False


async def log_request_hook(request: httpx.Request):
    logger.debug(f"--> HTTPX Request: {request.method} {request.url}")

    headers = {
        k: (v if k.lower() != "authorization" else "Bearer [MASKED]")
        for k, v in request.headers.items()
    }
    logger.debug(f"    Headers: {headers}")


async def log_response_hook(response: httpx.Response):
    logger.debug(
        f"<-- HTTPX Response: {response.status_code} ({response.reason_phrase}) for {response.url}"
    )
    if settings.LOG_LEVEL.upper() == "DEBUG":

        try:

            response_text = response.text
            logger.debug(
                f"    Body (first 500 chars): {response_text[:500]}{'...' if len(response_text) > 500 else ''}"
            )
        except:
            logger.debug("    Could not log response body")


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info(f"Starting up {settings.PROJECT_NAME}...")

    headers = {
        "Authorization": (
            f"Bearer {settings.PINEAPPLE_API_TOKEN}"
            if settings.PINEAPPLE_API_TOKEN
            else ""
        ),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    timeout = httpx.Timeout(25.0, connect=5.0)
    transport = httpx.AsyncHTTPTransport(retries=1)

    app.state.pineapple_client = httpx.AsyncClient(
        base_url=settings.PINEAPPLE_API_URL,
        headers=headers,
        timeout=timeout,
        transport=transport,
        event_hooks={
            "request": [log_request_hook],
            "response": [log_response_hook],
        },
    )
    logger.info(
        f"Pineapple HTTP client initialized for base URL: {settings.PINEAPPLE_API_URL}"
    )

    try:
        from app.db.session import get_supabase_client

        get_supabase_client()
    except Exception as e:
        logger.critical(f"Failed to initialize Supabase client on startup: {e}")

    yield

    logger.info("Shutting down...")
    if hasattr(app.state, "pineapple_client") and app.state.pineapple_client:
        await app.state.pineapple_client.aclose()
        logger.info("Pineapple HTTP client closed.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    description="API for creating insurance quotes and leads via Pineapple integration, with Supabase storage and auth.",
    version="2.0.0",
)


app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


logger.info(f"Configuring CORS for origins: {settings.BACKEND_CORS_ORIGINS}")


origins = []
if settings.BACKEND_CORS_ORIGINS == "*":
    origins = ["*"]
else:

    origins = [
        origin.strip()
        for origin in settings.BACKEND_CORS_ORIGINS.split(",")
        if origin.strip()
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": f"Rate limit exceeded: {exc.detail}"},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(
        f"Unhandled exception for request {request.method} {request.url}: {exc}"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."},
    )


app.include_router(api_router, prefix=settings.API_V1_STR)

if HAS_PINEAPPLE_ROUTES and pineapple_router is not None:
    app.include_router(pineapple_router, prefix="/api/v1/pineapple")
    logger.info("Pineapple routes added to the application")
else:
    logger.warning("Pineapple routes were not added to the application")


@app.get("/", tags=["Health"], summary="API Root/Health Check")
async def read_root(request: Request):
    """Basic health check endpoint. Confirms the API is running."""

    client_host = request.headers.get(
        "x-forwarded-for", request.client.host if request.client else "Unknown"
    )
    logger.info(f"Root endpoint '/' accessed by {client_host}")

    return {"message": f"Welcome to {settings.PROJECT_NAME}", "status": "healthy"}
