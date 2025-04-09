import logging
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, Request, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

# Rate Limiting Imports
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Import the centralized limiter
from app.core.rate_limiter import limiter

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging_config import setup_logging  # Import the setup function

# --- Initialize Logging ---
# Call this early, passing the log level from settings
setup_logging(log_level_str=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)  # Get logger after setup

# Initialize pineapple_router to None before attempting import
pineapple_router: APIRouter | None = None
HAS_PINEAPPLE_ROUTES = False

# Import the pineapple router if it exists, otherwise handle the import error gracefully
try:
    from app.api.routes.pineapple_routes import router as pineapple_router

    HAS_PINEAPPLE_ROUTES = pineapple_router is not None
    logger.info("Successfully imported Pineapple routes")
except ImportError as e:
    logger.warning(
        f"Pineapple routes module not found, will not include these endpoints: {e}"
    )
    HAS_PINEAPPLE_ROUTES = False


# --- Optional HTTPX Logging Hooks ---
async def log_request_hook(request: httpx.Request):
    logger.debug(f"--> HTTPX Request: {request.method} {request.url}")
    # Mask Authorization header if logging:
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
        # Only log response body in DEBUG mode
        try:
            # Try to get JSON response
            response_text = response.text
            logger.debug(
                f"    Body (first 500 chars): {response_text[:500]}{'...' if len(response_text) > 500 else ''}"
            )
        except:
            logger.debug("    Could not log response body")


# --- Lifespan for managing resources ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting up {settings.PROJECT_NAME}...")

    # Setup shared HTTP client for Pineapple API
    headers = {
        "Authorization": (
            f"Bearer {settings.PINEAPPLE_API_TOKEN}"
            if settings.PINEAPPLE_API_TOKEN
            else ""
        ),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    # Increased timeout slightly, adjust based on Pineapple's typical response time
    timeout = httpx.Timeout(25.0, connect=5.0)
    transport = httpx.AsyncHTTPTransport(retries=1)  # Simple retry

    # Store shared client in application state
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

    # Initialize Supabase client on startup (ensures connection early)
    try:
        from app.db.session import get_supabase_client

        get_supabase_client()  # Trigger initialization
    except Exception as e:
        logger.critical(f"Failed to initialize Supabase client on startup: {e}")
        # We'll continue anyway and let individual requests fail if needed

    yield  # Application runs here

    # Shutdown
    logger.info("Shutting down...")
    if hasattr(app.state, "pineapple_client") and app.state.pineapple_client:
        await app.state.pineapple_client.aclose()
        logger.info("Pineapple HTTP client closed.")


# --- Create FastAPI App ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,  # Use the lifespan context manager
    description="API for creating insurance quotes and leads via Pineapple integration, with Supabase storage and auth.",
    version="2.0.0",
)

# --- Apply Middleware (Order Matters!) ---

# 1. Rate Limiter State & Middleware
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)  # Executes before routing

# 2. CORS Middleware
# IMPORTANT: Restrict origins in production! Use settings.BACKEND_CORS_ORIGINS
logger.info(f"Configuring CORS for origins: {settings.BACKEND_CORS_ORIGINS}")

# Parse the CORS origins string
origins = []
if settings.BACKEND_CORS_ORIGINS == "*":
    origins = ["*"]  # Handle wildcard case
else:
    # Handle comma-separated list
    origins = [
        origin.strip()
        for origin in settings.BACKEND_CORS_ORIGINS.split(",")
        if origin.strip()
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow standard methods
    allow_headers=["*"],  # Allow standard headers + Authorization etc.
)


# --- Add Exception Handlers ---
# Rate limit exceeded handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": f"Rate limit exceeded: {exc.detail}"},
    )


# Optional: Global error handler for unexpected errors (catch-all)
# Customize this to avoid leaking internal details in production
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(
        f"Unhandled exception for request {request.method} {request.url}: {exc}"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected internal server error occurred."},
    )


# --- Include API Routers ---
app.include_router(api_router, prefix=settings.API_V1_STR)

# Add the pineapple router to the application only if it was successfully imported
if HAS_PINEAPPLE_ROUTES and pineapple_router is not None:
    app.include_router(pineapple_router, prefix="/api/v1/pineapple")
    logger.info("Pineapple routes added to the application")
else:
    logger.warning("Pineapple routes were not added to the application")


# --- Root Endpoint ---
@app.get("/", tags=["Health"], summary="API Root/Health Check")
async def read_root(request: Request):
    """Basic health check endpoint. Confirms the API is running."""
    # Note: request.client.host might be the proxy IP if behind one
    client_host = request.headers.get(
        "x-forwarded-for", request.client.host if request.client else "Unknown"
    )
    logger.info(f"Root endpoint '/' accessed by {client_host}")
    # Optionally add deeper health checks (e.g., test Supabase connection)
    return {"message": f"Welcome to {settings.PROJECT_NAME}", "status": "healthy"}


# --- Run instruction ---
# Use: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 [--log-level debug]
