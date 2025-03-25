from sqlmodel import SQLModel, Field
from typing import Optional

class LeadTransfer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lead_id: int = Field(..., index=True)
    transferred_to: str = Field(..., max_length=255)
    transfer_date: str = Field(..., max_length=10)  # Format: YYYY-MM-DD
    status: str = Field(..., max_length=50)  # e.g., 'pending', 'completed', 'failed'