from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    ConfigDict,
    field_validator,
    model_validator,
    NonNegativeInt,
    PositiveFloat,
    NonNegativeFloat,
)
from typing import List, Optional, Literal, Union, Any, Dict
from datetime import date, datetime

# --- Pineapple API Specific Schemas ---


class PineappleAddress(BaseModel):
    model_config = ConfigDict(extra="allow")
    addressLine: str = Field(..., description="The main address line")
    postalCode: int = Field(..., description="Postal code")
    suburb: str = Field(..., description="Suburb name")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")


class PineappleRegularDriver(BaseModel):
    model_config = ConfigDict(extra="allow")

    maritalStatus: Literal[
        "Single", "Married", "Divorced", "Widowed", "LivingTogether", "Annulment"
    ]
    currentlyInsured: bool
    yearsWithoutClaims: NonNegativeInt  # Use specific types
    relationToPolicyHolder: Literal["Self", "Spouse", "Child", "Other"]
    emailAddress: Optional[EmailStr] = None
    mobileNumber: Optional[str] = None
    idNumber: Optional[str] = Field(None, description="Driver's ZA ID number")
    prvInsLosses: Optional[NonNegativeInt] = Field(
        None, description="Number of previous insurance losses"
    )
    licenseIssueDate: Optional[date] = None
    dateOfBirth: Optional[date] = None

    # Pydantic V2 model validator (runs after field validation)
    @model_validator(mode="after")
    def check_id_or_dob(self) -> "PineappleRegularDriver":
        if not self.idNumber and not self.dateOfBirth:
            # Consider if this validation is strictly required by Pineapple or optional
            # If strictly required:
            # raise ValueError('Either idNumber or dateOfBirth must be provided for the driver')
            pass  # Make it optional based on API docs unless confirmed otherwise
        return self


class PineappleVehicle(BaseModel):
    model_config = ConfigDict(extra="allow")

    year: int = Field(..., gt=1900, lt=date.today().year + 2)
    make: str
    model: str
    mmCode: Optional[str] = None
    modified: Literal["Y", "N"]
    category: Literal[
        "SUV",
        "HB",
        "SD",
        "CP",
        "SAV",
        "DC",
        "SC",
        "MPV",
        "CB",
        "SW",
        "XO",
        "HT",
        "RV",
        "CC",
        "PV",
        "BS",
        "DS",
    ]
    colour: str
    engineSize: Optional[PositiveFloat] = None  # Use specific types
    financed: Literal["Y", "N"]
    owner: Literal["Y", "N"]
    status: Literal["New", "SecondHand"]
    partyIsRegularDriver: Literal["Y", "N"]
    accessories: Literal["Y", "N"]
    accessoriesAmount: Optional[NonNegativeFloat] = None
    retailValue: NonNegativeFloat
    marketValue: Optional[NonNegativeFloat] = None
    insuredValueType: Literal["Retail", "Market"]
    useType: Literal["Private", "Commercial", "BusinessUse"]
    overnightParkingSituation: Literal["Garage", "Carport", "InTheOpen", "Unconfirmed"]
    coverCode: Literal["Comprehensive"]  # Assuming only comprehensive
    address: PineappleAddress
    regularDriver: PineappleRegularDriver

    # Pydantic V2 field validator (example)
    @field_validator("accessoriesAmount")
    @classmethod
    def check_accessories_amount(cls, v: Optional[float], info) -> Optional[float]:
        # info.data contains the data for the whole model being validated
        if "accessories" in info.data and info.data["accessories"] == "Y":
            if v is None or v <= 0:
                raise ValueError(
                    'accessoriesAmount must be positive if accessories is "Y"'
                )
        elif "accessories" in info.data and info.data["accessories"] == "N":
            if v is not None and v > 0:
                # Optional: Enforce amount is 0 or None if accessories is 'N'
                # raise ValueError('accessoriesAmount must be 0 or null if accessories is "N"')
                pass  # Allow non-zero amount even if accessories=N, Pineapple might handle it
        return v


class PineappleQuickQuoteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")  # Strict request structure to Pineapple
    source: str
    externalReferenceId: str
    vehicles: List[PineappleVehicle]


class PineappleQuoteDataItem(BaseModel):
    model_config = ConfigDict(
        extra="allow"
    )  # Allow extra fields from response data part
    premium: float
    excess: float


class PineappleQuickQuoteResponse(BaseModel):
    model_config = ConfigDict(extra="allow")  # Allow extra fields from response
    success: bool
    id: Optional[str] = None
    data: Optional[List[PineappleQuoteDataItem]] = None
    message: Optional[str] = None  # Capture potential error messages


# --- Schemas for our API Endpoints ---
class QuoteRequestVehicle(PineappleVehicle):
    # Inherit V2 config and validation
    # Forbid extra fields coming *into* our API for this vehicle part
    model_config = ConfigDict(extra="forbid")


class QuoteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")  # Be strict on overall input structure
    vehicles: List[QuoteRequestVehicle]
    # user_reference: Optional[str] = None # Optional field if needed


class QuoteResponseData(BaseModel):
    # Data part of *our* API response
    model_config = ConfigDict(
        from_attributes=True
    )  # If created from DB/ORM model or another Pydantic model
    premium: float
    excess: float


class QuoteResponse(BaseModel):
    # Overall response from *our* API
    model_config = ConfigDict(from_attributes=True)
    success: bool
    quote_id: Optional[str] = Field(None, description="ID needed for lead transfer")
    quote_data: Optional[List[QuoteResponseData]] = None
    message: Optional[str] = None
    local_quote_reference_id: Optional[str] = Field(
        None, description="Internal reference ID"
    )


# --- Schemas for Local Storage (Supabase 'quotes' Table) ---
class QuoteRecordBase(BaseModel):
    # Base fields for quote record, used for creation and reading
    user_id: str  # Typically UUID string from Supabase Auth
    request_details: Dict[str, Any]  # Store the incoming QuoteRequest data as dict
    status: str = (
        "pending"  # e.g., pending_external, success, failed_external, failed_internal
    )


class QuoteRecordCreate(QuoteRecordBase):
    # Schema for data used to *create* a record
    model_config = ConfigDict(extra="allow")  # Allow setting ID if using client UUIDs
    id: Optional[str] = None  # Primary Key - Can be set if using client-generated UUIDs


class QuoteRecordUpdate(BaseModel):
    # Schema for data used to *update* a record (all fields optional)
    model_config = ConfigDict(
        extra="forbid"
    )  # Don't allow arbitrary fields for update payload

    status: Optional[str] = None
    pineapple_quote_id: Optional[str] = None
    premium: Optional[float] = None
    excess: Optional[float] = None
    response_details: Optional[Dict[str, Any]] = (
        None  # Store full Pineapple response dict
    )
    error_message: Optional[str] = None


class QuoteRecord(QuoteRecordBase):
    # Represents a full quote record read from the database
    model_config = ConfigDict(
        from_attributes=True, extra="ignore"
    )  # Read from DB, ignore extra DB cols

    id: str  # Primary key from Supabase (e.g., UUID string)
    pineapple_quote_id: Optional[str] = None  # The ID returned by Pineapple
    premium: Optional[float] = None
    excess: Optional[float] = None
    response_details: Optional[Dict[str, Any]] = None  # Full Pineapple response
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None  # Timestamps from Supabase
    updated_at: Optional[datetime] = None
