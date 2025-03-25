from typing import Generic, List, TypeVar, Optional
from pydantic import BaseModel, Field
from fastapi import Query

T = TypeVar("T")


class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(10, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.limit = limit
        self.skip = (page - 1) * limit


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Generic paginated response model for any type of data
    """

    items: List[T]
    total: int
    page: int
    size: int
    pages: Optional[int] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.size > 0:
            self.pages = (self.total + self.size - 1) // self.size
        else:
            self.pages = 0
