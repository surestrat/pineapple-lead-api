from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import enum


class LeadStatusEnum(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class Lead(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., index=True)
    email: str = Field(..., index=True)
    phone: Optional[str] = Field(default=None)
    company: Optional[str] = Field(default=None)
    status: str = Field(default=LeadStatusEnum.NEW, index=True)
    source: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    owner_id: Optional[int] = Field(default=None, index=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, index=True)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, index=True)

    # If using relationships
    # quotes: List["Quote"] = Relationship(back_populates="lead")

    def __repr__(self):
        return f"Lead(id={self.id}, name={self.name}, email={self.email}, status={self.status})"
