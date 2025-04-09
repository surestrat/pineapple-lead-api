from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any, Union, Literal


class LeadTransferRequest(BaseModel):
    """Model for lead transfer request to Pineapple API."""

    model_config = ConfigDict(extra="allow")  # Added to allow extra fields

    source: str = Field(default="SureStrat", description="Lead source or campaign name")
    first_name: str = Field(..., description="Lead's first name")
    last_name: str = Field(..., description="Lead's last name")
    email: EmailStr = Field(..., description="Lead's email address")
    id_number: Optional[str] = Field(None, description="Optional ZA ID number")
    quote_id: Optional[str] = Field(
        None, description="Quote ID returned from Quick Quote endpoint"
    )
    contact_number: str = Field(..., description="Contact phone number")


class LeadTransferData(BaseModel):
    """Model for lead transfer response data."""

    model_config = ConfigDict(extra="allow")

    uuid: str
    redirect_url: Optional[str] = None


class LeadTransferResponse(BaseModel):
    """Model for lead transfer response from Pineapple API."""

    model_config = ConfigDict(extra="allow")  # Added to allow extra fields

    success: bool
    data: Optional[LeadTransferData] = None
    message: Optional[str] = None


class Address(BaseModel):
    """Vehicle address model."""

    model_config = ConfigDict(extra="allow")  # Added to allow extra fields

    addressLine: str
    postalCode: int
    suburb: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RegularDriver(BaseModel):
    """Regular driver information model."""

    model_config = ConfigDict(extra="allow")  # Added to allow extra fields

    maritalStatus: str = Field(..., description="Marital status of the driver")
    currentlyInsured: bool
    yearsWithoutClaims: int
    relationToPolicyHolder: str
    emailAddress: EmailStr
    mobileNumber: str
    idNumber: Optional[str] = None
    prvInsLosses: Optional[int] = 0
    licenseIssueDate: Optional[str] = None
    dateOfBirth: Optional[str] = None


class Vehicle(BaseModel):
    """Vehicle information model for quick quote."""

    model_config = ConfigDict(extra="allow")  # Added to allow extra fields

    year: int
    make: str
    model: str
    mmCode: Optional[str] = None
    modified: str = Field(..., pattern="^[YN]$")
    category: str
    colour: str
    engineSize: Optional[float] = None
    financed: str = Field(..., pattern="^[YN]$")
    owner: str = Field(..., pattern="^[YN]$")
    status: str
    partyIsRegularDriver: str = Field(..., pattern="^[YN]$")
    accessories: str = Field(..., pattern="^[YN]$")
    accessoriesAmount: Optional[int] = 0
    retailValue: int
    marketValue: Optional[int] = None
    insuredValueType: str
    useType: str
    overnightParkingSituation: str
    coverCode: str
    address: Address
    regularDriver: RegularDriver


class QuickQuoteRequest(BaseModel):
    """Model for quick quote request to Pineapple API."""

    model_config = ConfigDict(extra="allow")  # Added to allow extra fields

    source: str = Field(default="SureStrat")
    externalReferenceId: str
    vehicles: List[Vehicle]


class QuoteResult(BaseModel):
    """Model for individual quote result."""

    model_config = ConfigDict(extra="allow")  # Added to allow extra fields

    premium: float
    excess: float  # Changed from int to float for compatibility


class QuickQuoteResponse(BaseModel):
    """Model for quick quote response from Pineapple API."""

    model_config = ConfigDict(extra="allow")  # Added to allow extra fields

    success: bool
    id: Optional[str] = None
    data: Optional[List[QuoteResult]] = None
    message: Optional[str] = None
