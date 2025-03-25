# app/api/__init__.py

from fastapi import APIRouter

from .lead_transfer.router import router as lead_transfer_router
from .quick_quote.router import router as quick_quote_router

router = APIRouter()

router.include_router(lead_transfer_router, prefix="/leads", tags=["leads"])
router.include_router(quick_quote_router, prefix="/quotes", tags=["quotes"])