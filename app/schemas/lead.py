from sqlmodel import SQLModel
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, ClassVar
from datetime import datetime


class LeadBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9\s\-()]+$")
    company: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field("new")
    source: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("name")
    def name_must_contain_space(cls, v):
        if " " not in v:
            raise ValueError("name must contain at least first and last name")
        return v


class LeadCreate(LeadBase):
    pass


class LeadRead(LeadBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    owner_id: Optional[int] = None

    model_config = {"from_attributes": True}


class LeadUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r"^\+?[0-9\s\-()]+$")
    company: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    owner_id: Optional[int] = None


class LeadTransferRequest(BaseModel):
    lead_id: int = Field(..., gt=0)
    new_owner_id: int = Field(..., gt=0)


class LeadTransferResponse(BaseModel):
    lead_id: int
    new_owner_id: int
    status: str = "transferred"
    transfer_date: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


# Pineapple API specific schemas
class PineappleLeadTransferRequest(BaseModel):
    source: str = Field(..., description="Lead source or campaign name")
    first_name: str = Field(..., description="Lead's first name")
    last_name: str = Field(..., description="Lead's last name")
    email: EmailStr = Field(..., description="Lead's email address")
    id_number: Optional[str] = Field(None, description="ZA ID number")
    quote_id: Optional[str] = Field(
        None, description="Quote ID returned from Quick Quote API"
    )
    contact_number: str = Field(..., description="Contact phone number")


class PineappleLeadTransferResponse(BaseModel):
    success: bool
    uuid: str
    redirect_url: str


# For backwards compatibility
LeadResponse = LeadRead
LeadSchema = LeadBase
