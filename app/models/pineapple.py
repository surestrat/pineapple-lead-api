from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any


class LeadTransferRequest(BaseModel):
    """Model for lead transfer request to Pineapple API."""

    source: str = Field(
        default="CrispSolutions", description="Lead source or campaign name"
    )
    first_name: str = Field(..., description="Lead's first name")
    last_name: str = Field(..., description="Lead's last name")
    email: EmailStr = Field(..., description="Lead's email address")
    id_number: Optional[str] = None
    quote_id: Optional[str] = None
    contact_number: str


class LeadTransferResponse(BaseModel):
    """Model for lead transfer response from Pineapple API."""

    success: bool
    data: Dict[str, Any]


class Address(BaseModel):
    """Vehicle address model."""

    addressLine: str
    postalCode: int
    suburb: str
    latitude: float
    longitude: float


class RegularDriver(BaseModel):
    """Regular driver information model."""

    maritalStatus: str
    currentlyInsured: bool
    yearsWithoutClaims: int
    relationToPolicyHolder: str
    emailAddress: EmailStr
    mobileNumber: str
    idNumber: str
    prvInsLosses: int
    licenseIssueDate: str
    dateOfBirth: str


class Vehicle(BaseModel):
    """Vehicle information model for quick quote."""

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


class QuickQuoteRequest(BaseModel):
    """Model for quick quote request to Pineapple API."""

    source: str = Field(default="CrispSolutions")
    externalReferenceId: str
    vehicles: List[Vehicle]


class QuoteResult(BaseModel):
    """Model for individual quote result."""

    premium: float
    excess: int


class QuickQuoteResponse(BaseModel):
    """Model for quick quote response from Pineapple API."""

    success: bool
    id: str
    data: List[QuoteResult]
