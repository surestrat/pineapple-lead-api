# app/db/repositories/__init__.py

from .base import BaseRepository
from .lead_repository import LeadRepository
from .quote_repository import QuoteRepository

__all__ = ["BaseRepository", "LeadRepository", "QuoteRepository"]