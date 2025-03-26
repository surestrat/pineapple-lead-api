from fastapi import FastAPI
from app.routes import leads, quotes, auth
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.utils.logger import logger
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.auth_middleware import BearerTokenMiddleware

app = FastAPI(
    title="Pineapple Lead API",
    description="API for managing leads and quotes for insurance products",
    version="2.0.0",
    docs_url="/",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Leads",
            "description": "Operations with customer leads",
        },
        {
            "name": "Quotes",
            "description": "Operations with insurance quotes",
        },
        {
            "name": "Authentication",
            "description": "Authentication and authorization endpoints",
        },
    ],
    contact={
        "name": "Support Team",
        "email": "support@surestrat.co.za",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://example.com/license",
    },
)
limiter = Limiter(key_func=lambda: "global")  # or another key function
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Add bearer token middleware
app.add_middleware(BearerTokenMiddleware)


async def _rate_limit_exceeded_handler(request: Request, exc: Exception):
    """Handler for rate limit exceeded exceptions.

    Args:
        request (Request): The FastAPI request object containing client request details
        exc (Exception): The rate limit exception that was raised

    Returns:
        JSONResponse: A JSON response with 429 status code and error message

    Examples:
        This handler is automatically called when rate limits are exceeded:
        >>> response = _rate_limit_exceeded_handler(request, RateLimitExceeded())
        >>> response.status_code
        429
    """
    client_ip = request.client.host if request.client else "unknown"
    endpoint = request.url.path
    logger.warning(
        f"Rate limit exceeded: {exc}. Client IP: {client_ip}, Endpoint: {endpoint}"
    )
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded",
            "endpoint": endpoint,
        },
    )


app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for request validation exceptions.

    Args:
        request (Request): The FastAPI request object
        exc (RequestValidationError): The validation exception that was raised

    Returns:
        JSONResponse: A JSON response with 422 status code and validation error details

    Examples:
        This handler is automatically called when request validation fails:
        >>> response = validation_exception_handler(request, validation_error)
        >>> response.status_code
        422
    """
    logger.error(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


app.include_router(leads.router, prefix="/api/v1/leads", tags=["Leads"])
app.include_router(quotes.router, prefix="/api/v1/quotes", tags=["Quotes"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])


@app.get("/health")
async def health_check():
    """Performs an API health check.

    Returns:
        dict: A dictionary containing the API status

    Examples:
        >>> response = await health_check()
        >>> response
        {'status': 'ok'}
    """
    return {"status": "ok"}


logger.info("FastAPI application started.")
