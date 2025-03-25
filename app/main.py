from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.api.healthcheck import router as healthcheck_router
import logging
import time
import sys
import logging.config
import os
from sqlmodel import SQLModel
from app.db.base import async_engine
from sqlalchemy import text
from app.models import lead, quote  # Import models to ensure they're registered

# Set up logging
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "default",
                "level": "INFO",
            }
        },
        "root": {"handlers": ["console"], "level": "INFO"},
    }
)

# Create logger for this module
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API for managing leads and generating quotes",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add static files middleware before other middleware
from fastapi.staticfiles import StaticFiles

# Create static directory if it doesn't exist
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)

# Mount static files directory
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Add CORS middleware with proper allowed_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Request to {request.url.path} processed in {process_time:.4f}s")
    return response


# Register exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(healthcheck_router, tags=["system"])
app.include_router(api_router, prefix=settings.API_V1_STR)


# Customized docs endpoint with authentication
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    if app.openapi_url is None:
        app.openapi_url = "/openapi.json"
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{settings.PROJECT_NAME} - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    logger.info("Test endpoint called")
    return {"status": "ok", "message": "API is working"}


async def init_database():
    """Initialize database and create tables"""
    try:
        async with async_engine.begin() as conn:
            logger.info("Creating database tables...")
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        return False


async def check_database():
    """Check database connection and verify tables exist"""
    try:
        async with async_engine.connect() as conn:
            # Test basic connection
            await conn.execute(text("SELECT 1"))

            # Check if tables exist
            result = await conn.execute(
                text(
                    """SELECT name FROM sqlite_master 
                WHERE type='table' AND 
                name IN ('lead', 'quote')"""
                )
            )
            tables = result.fetchall()

            if len(tables) < 2:
                logger.warning("Missing required tables")
                return False

            logger.info("Database connection and tables verified")
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False


@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting up {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Server running on port: {settings.port}")

    # Initialize and verify database
    if not await init_database():
        raise RuntimeError("Database initialization failed")

    if not await check_database():
        raise RuntimeError("Database health check failed")

    logger.info("Database initialization and health check completed successfully")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.port)
