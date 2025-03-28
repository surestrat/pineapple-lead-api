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
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi
import fastapi
import os
import sys
from app.config.settings import Settings
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
from datetime import datetime


# Add this at the beginning, before creating the FastAPI app
def check_environment():
    """Check environment variables and abort if critical ones are missing"""
    from app.config.settings import settings

    critical_vars = [
        ("APPWRITE_ENDPOINT", settings.appwrite_endpoint),
        ("APPWRITE_PROJECT_ID", settings.appwrite_project_id),
        ("API_BEARER_TOKEN", settings.api_bearer_token),
    ]

    missing = []
    for name, value in critical_vars:
        if value is None or "YOUR_" in value or value == "your-bearer-token":
            missing.append(name)

    if missing:
        print(
            "ERROR: Critical environment variables are missing or have default values:"
        )
        for var in missing:
            print(f"  - {var}")
        print("\nPlease check your .env file configuration.")
        print("You can run python validate_env.py to diagnose the issue.")
        sys.exit(1)

    # Verify API token format for Pineapple API
    if (
        "KEY=" not in settings.api_bearer_token
        or "SECRET=" not in settings.api_bearer_token
    ):
        print(
            "WARNING: API_BEARER_TOKEN may not be properly formatted for Pineapple API."
        )
        print("It should be in format: KEY=xxx SECRET=xxx")
        print(
            f"Current format: {settings.api_bearer_token[:10]}... ({len(settings.api_bearer_token)} chars)"
        )
        print("Pineapple API calls may fail with this token format.")
        # Don't exit, just warn


# Run the check before initializing the app
check_environment()

# Log system information on startup
logger.info("====== SYSTEM INFORMATION ======")
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Environment variables: {list(os.environ.keys())}")
logger.info("===============================")

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
    openapi_url="/api/v1/openapi.json",
)
limiter = Limiter(key_func=lambda: "global")  # or another key function
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Configure CORS first
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add bearer token middleware - only for logging, not for enforcement
app.add_middleware(BearerTokenMiddleware)

# Security scheme for Swagger UI - keep this for documentation but don't enforce it
security_scheme = HTTPBearer(auto_error=False)
app.swagger_ui_init_oauth = {
    "usePkceWithAuthorizationCodeGrant": True,
    "clientId": "webClient",
    "clientSecret": "",
    "scopeSeparator": " ",
    "useBasicAuthenticationWithAccessCodeGrant": False,
}

# Security scheme configuration
app.openapi_schema = None
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", scopes={})


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter the JWT token you received from the /api/v1/auth/token endpoint",
        }
    }

    # Apply security globally - this adds the Authorization button to Swagger UI
    openapi_schema["security"] = [{"bearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


async def _rate_limit_exceeded_handler(request: Request, exc: Exception):
    """Handler for rate limit exceeded exceptions."""
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for request validation exceptions."""
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
    """Performs an API health check."""
    health_info = {
        "status": "ok",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "appwrite": {"status": "unknown", "endpoint": Settings.appwrite_endpoint},
            "pineapple": {
                "status": "unknown",
                "endpoint": Settings.pineapple_api_base_url,
            },
        },
    }

    # Check environment variables
    if "YOUR_" in Settings.appwrite_endpoint or not Settings.appwrite_endpoint:
        health_info["services"]["appwrite"]["status"] = "misconfigured"
    else:
        health_info["services"]["appwrite"]["status"] = "configured"

    # Check Pineapple API token format
    api_token = Settings.api_bearer_token
    if "KEY=" in api_token and "SECRET=" in api_token:
        health_info["services"]["pineapple"]["status"] = "configured"
        health_info["services"]["pineapple"]["token_format"] = "KEY=xxx SECRET=xxx"
    else:
        health_info["services"]["pineapple"]["status"] = "warning"
        health_info["services"]["pineapple"]["token_format"] = "non-standard"

    return health_info


@app.on_event("startup")
async def startup_event():
    """Log important information when the application starts"""
    from app.utils.logger import logger
    from app.config.settings import settings

    logger.info("====== FASTAPI APPLICATION STARTED ======")
    logger.info(f"FastAPI version: {fastapi.__version__}")
    logger.info(f"Host: {os.environ.get('HOST', '0.0.0.0')}")
    logger.info(f"Port: {os.environ.get('PORT', '8000')}")
    logger.info(f"Log level: {settings.log_level}")
    logger.info(f"Environment: {os.environ.get('ENV', 'development')}")

    # Log auth-related settings
    logger.info(f"Auth test_username: '{settings.test_username}'")
    logger.info(
        f"Auth test_password length: {len(settings.test_password) if settings.test_password else 0}"
    )
    logger.info(f"Using algorithm: {settings.algorithm}")

    # Log critical services configuration
    logger.info(f"Appwrite endpoint: {settings.appwrite_endpoint}")
    logger.info(f"Pineapple API base URL: {settings.pineapple_api_base_url}")
    logger.info(f"Protected endpoints: {settings.protected_endpoints}")

    # Check for default values that might indicate environment loading issues
    if "YOUR_" in settings.appwrite_endpoint:
        logger.warning(
            "Using default placeholder Appwrite endpoint. Check your environment variables!"
        )
    if "your-bearer-token" == settings.api_bearer_token:
        logger.warning(
            "Using default placeholder API bearer token. Check your environment variables!"
        )

    # Verify Pineapple API token
    api_token = settings.api_bearer_token
    token_valid = "KEY=" in api_token and "SECRET=" in api_token

    if token_valid:
        logger.info("✅ Pineapple API token format is valid (contains KEY and SECRET)")
    else:
        if not api_token:
            logger.error("❌ Pineapple API token is missing!")
        elif "KEY=" not in api_token:
            logger.warning("⚠️ Pineapple API token missing KEY= prefix")
        elif "SECRET=" not in api_token:
            logger.warning("⚠️ Pineapple API token missing SECRET= part")
        else:
            logger.warning("⚠️ Pineapple API token format is non-standard")

    logger.info("=======================================")
    logger.info("FastAPI application started.")


# Configure static files
# Create static files directory if it doesn't exist
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(parents=True, exist_ok=True)

# Copy swagger helper script if it doesn't exist
swagger_helper_path = static_dir / "swagger-helper.js"
if not swagger_helper_path.exists():
    with open(swagger_helper_path, "w") as f:
        f.write(
            """
// Swagger UI Helper - Adds token management functionality
// ...content of swagger-helper.js...
        """
        )

# Mount static files
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Custom HTML for root to include the helper script
@app.get("/", include_in_schema=False)
async def custom_swagger_ui_html():
    return HTMLResponse(
        """<!DOCTYPE html>
<html>
<head>
    <title>Pineapple Lead API</title>
    <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
        const ui = SwaggerUIBundle({
            url: '/api/v1/openapi.json',
            dom_id: '#swagger-ui',
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.SwaggerUIStandalonePreset
            ],
            layout: "BaseLayout",
            deepLinking: true,
            showExtensions: true,
            showCommonExtensions: true
        });
    </script>
    <script src="/static/swagger-helper.js"></script>
</body>
</html>"""
    )
