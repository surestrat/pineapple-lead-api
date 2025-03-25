from fastapi import APIRouter
from app.api.lead_transfer.router import router as lead_transfer_router
from app.api.quick_quote.router import router as quick_quote_router
from app.api.healthcheck import router as healthcheck_router

api_router = APIRouter()

api_router.include_router(lead_transfer_router, prefix="/leads", tags=["leads"])
api_router.include_router(quick_quote_router, prefix="/quotes", tags=["quotes"])
api_router.include_router(healthcheck_router, tags=["system"])
