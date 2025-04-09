from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    ConfigDict,
    validator,
)  # Keep validator if needed for older versions
from pydantic import (
    field_validator,
    model_validator,
    FieldValidationInfo,
)  # V2 validators
from typing import Optional, List, Dict, Any
from datetime import datetime  # Added datetime

# --- Pineapple API Specific Schemas ---


class PineappleLeadTransferRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")  # Strict request structure to Pineapple

    source: str  # Will be set from config
    first_name: str
    last_name: str
    email: EmailStr  # Marked as unique and required by Pineapple
    id_number: Optional[str] = Field(None, description="Optional ZA ID number")
    quote_id: Optional[str] = Field(None, description="ID from Quick Quote response")
    contact_number: Optional[str] = None


class PineappleLeadTransferData(BaseModel):
    model_config = ConfigDict(
        extra="allow"
    )  # Allow extra fields from Pineapple response data part
    uuid: str
    redirect_url: Optional[str] = None


class PineappleLeadTransferResponse(BaseModel):
    model_config = ConfigDict(
        extra="allow"
    )  # Allow extra fields from Pineapple response
    success: bool
    data: Optional[PineappleLeadTransferData] = None
    message: Optional[str] = None  # Capture potential error messages


# --- Schemas for our API Endpoints ---


class LeadCreate(BaseModel):
    # Input to our API's lead creation/transfer endpoint
    model_config = ConfigDict(extra="forbid")  # Strict input structure

    first_name: str
    last_name: str
    email: EmailStr
    id_number: Optional[str] = None
    contact_number: Optional[str] = None
    # This is crucial: The client needs to provide the ID from a successful quote
    quote_id: str = Field(
        ..., description="The quote ID received from the /quotes/quick endpoint"
    )
    # Optionally link to the internal quote record
    local_quote_reference_id: Optional[str] = Field(
        None, description="Optional internal quote reference from the quote response"
    )


class LeadResponse(BaseModel):
    # Response from *our* API after attempting lead transfer
    model_config = ConfigDict(from_attributes=True)  # Enable reading from objects/dicts

    success: bool
    lead_uuid: Optional[str] = None  # The UUID from Pineapple
    redirect_url: Optional[str] = None
    message: Optional[str] = None
    local_lead_reference_id: Optional[str] = Field(
        None, description="Internal reference ID for the created lead record"
    )


# --- Schemas for Local Storage (Supabase 'leads' Table) ---


class LeadRecordBase(BaseModel):
    # Base fields for lead record
    user_id: str  # Link to the authenticated Supabase user
    quote_id: str  # The Pineapple quote_id used for transfer
    local_quote_reference_id: Optional[str] = None  # Link to our internal quote record
    first_name: str
    last_name: str
    email: EmailStr
    id_number: Optional[str] = None
    contact_number: Optional[str] = None
    status: str = (
        "pending_transfer"  # e.g., pending_transfer, transferred, failed_transfer, failed_internal
    )


class LeadRecordCreate(LeadRecordBase):
    # Schema for creating a record
    model_config = ConfigDict(extra="allow")  # Allow setting ID if using client UUIDs
    id: Optional[str] = None  # Primary Key - Can be set if using client-generated UUIDs


class LeadRecordUpdate(BaseModel):
    # Schema for updating a record (all fields optional)
    model_config = ConfigDict(extra="forbid")

    status: Optional[str] = None
    pineapple_lead_uuid: Optional[str] = None  # The UUID returned by Pineapple
    pineapple_redirect_url: Optional[str] = None
    transfer_response: Optional[Dict[str, Any]] = (
        None  # Store the full Pineapple response dict
    )
    error_message: Optional[str] = None


class LeadRecord(LeadRecordBase):
    # Represents a full lead record read from the database
    model_config = ConfigDict(
        from_attributes=True, extra="ignore"
    )  # Read from DB, ignore extra DB cols

    id: str  # Primary key from Supabase (e.g., UUID string)
    pineapple_lead_uuid: Optional[str] = None
    pineapple_redirect_url: Optional[str] = None
    transfer_response: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None  # Timestamps from Supabase
    updated_at: Optional[datetime] = None
