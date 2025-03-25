from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class Quote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lead_id: int = Field(..., foreign_key="lead.id", index=True)
    quote_amount: float = Field(..., description="The amount of the quote", gt=0)
    quote_description: Optional[str] = Field(
        default=None, description="Description of the quote"
    )
    currency: str = Field(default="USD", description="Currency of the quote amount")
    valid_until: Optional[datetime] = Field(
        default=None, description="Date until quote is valid"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the quote was created",
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the quote was last updated",
    )

    # If using relationships
    # lead: Optional[Lead] = Relationship(back_populates="quotes")

    def __repr__(self):
        return (
            f"Quote(id={self.id}, amount={self.quote_amount}, lead_id={self.lead_id})"
        )
