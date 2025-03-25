from sqlmodel import SQLModel
from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional, ClassVar, List, Dict, Any, Union
from datetime import datetime, timedelta


class QuoteBase(BaseModel):
    description: str = Field(..., min_length=5, max_length=500)
    amount: float = Field(..., gt=0)
    currency: str = Field("USD", min_length=3, max_length=3)
    valid_until: Optional[datetime] = None

    @field_validator("valid_until", mode="before")
    def set_valid_until(cls, v):
        if v is None:
            # Default validity: 30 days from now
            return datetime.utcnow() + timedelta(days=30)
        return v

    @field_validator("currency")
    def currency_must_be_valid(cls, v):
        allowed_currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "ZAR"]
        if v not in allowed_currencies:
            raise ValueError(
                f"Currency must be one of: {', '.join(allowed_currencies)}"
            )
        return v


class QuoteCreate(QuoteBase):
    lead_id: int = Field(..., gt=0)


class QuoteRead(QuoteBase):
    id: int
    lead_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class QuoteUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=5, max_length=500)
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    valid_until: Optional[datetime] = None

    @field_validator("currency")
    def currency_must_be_valid(cls, v):
        if v is None:
            return v
        allowed_currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "ZAR"]
        if v not in allowed_currencies:
            raise ValueError(
                f"Currency must be one of: {', '.join(allowed_currencies)}"
            )
        return v


# Pineapple API specific schemas
class Address(BaseModel):
    addressLine: str
    postalCode: int
    suburb: str
    latitude: float
    longitude: float


class RegularDriver(BaseModel):
    maritalStatus: str
    currentlyInsured: bool
    yearsWithoutClaims: int
    relationToPolicyHolder: str
    emailAddress: str
    mobileNumber: str
    idNumber: str
    prvInsLosses: int
    licenseIssueDate: str
    dateOfBirth: str


class Vehicle(BaseModel):
    year: int
    make: str
    model: str
    mmCode: str
    modified: str
    category: str
    colour: str
    engineSize: float
    financed: str
    owner: str
    status: str
    partyIsRegularDriver: str
    accessories: str
    accessoriesAmount: int
    retailValue: int
    marketValue: int
    insuredValueType: str
    useType: str
    overnightParkingSituation: str
    coverCode: str
    address: Address
    regularDriver: RegularDriver


class PineappleQuickQuoteRequest(BaseModel):
    source: str
    externalReferenceId: str
    vehicles: List[Vehicle]


class QuoteResult(BaseModel):
    premium: float
    excess: int


class PineappleQuickQuoteResponse(BaseModel):
    success: bool
    id: str
    data: List[QuoteResult]


# For compatibility with the router
QuoteResponse = QuoteRead

# For backwards compatibility
QuoteSchema = QuoteBase
