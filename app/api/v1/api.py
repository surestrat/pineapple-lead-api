from fastapi import APIRouter

from app.api.v1.endpoints import auth, quotes, leads

api_router = APIRouter()

# Include routers from endpoint modules
# Add specific dependencies like rate limiting here if applying to whole router
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(quotes.router, prefix="/quotes", tags=["quotes"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])


# Example: Add a simple health check within the v1 prefix
@api_router.get("/health", status_code=200, tags=["Health"])
async def health_check():
    return {"status": "ok", "version": "v1"}
