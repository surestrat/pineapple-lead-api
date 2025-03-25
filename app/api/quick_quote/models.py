from sqlmodel import SQLModel, Field
from typing import Optional


class QuickQuote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lead_id: int
    quote_amount: float
    quote_description: str
    created_at: Optional[str] = Field(
        default=None, index=True
    )  # Use a proper datetime type in production
    updated_at: Optional[str] = Field(
        default=None, index=True
    )  # Use a proper datetime type in production

    # SQLModel already includes Config with orm_mode=True
