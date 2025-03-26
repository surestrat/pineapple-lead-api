from typing import Optional
from pydantic import BaseModel, Field


class LeadTransferRequest(BaseModel):
    """Pydantic model for lead transfer request validation.
    This class defines the schema for incoming lead transfer requests, ensuring all required
    fields are present and properly formatted before processing.
    Attributes:
        source (str): Lead source or campaign name (e.g., Hippo, SureStrat).
        first_name (str): Lead's first name.
        last_name (str): Lead's last name.
        email (str): Lead's email (unique and required).
        id_number (Optional[str]): Optional ZA ID number.
        quote_id (Optional[str]): ID returned from the Quick Quote endpoint (optional).
        contact_number (str): Contact phone number.
    """

    source: str = Field(
        ..., description="Lead source or campaign name (e.g., Hippo, SureStrat)"
    )
    first_name: str = Field(..., description="Lead's first name")
    last_name: str = Field(..., description="Lead's last name")
    email: str = Field(..., description="Lead's email (unique and required)")
    id_number: Optional[str] = Field(None, description="Optional ZA ID number")
    quote_id: Optional[str] = Field(
        None, description="This is returned from the Quick Quote endpoint (optional)"
    )
    contact_number: str = Field(..., description="Contact phone number")


class LeadTransferResponseData(BaseModel):
    """Response model for lead transfer operations.
    This model represents the data returned after a successful lead transfer operation.
    Attributes:
        uuid (str): Unique identifier for the lead.
        redirect_url (str): URL to redirect the user to after the lead transfer.
    """

    uuid: str = Field(..., description="Unique identifier for the lead")
    redirect_url: str = Field(..., description="URL to redirect the user to")


class LeadTransferResponse(BaseModel):
    """
    Response model for lead transfer operations.
    This model represents the structure of the response returned after attempting
    to transfer a lead. It includes a success indicator and detailed response data.
    Attributes:
        success (bool): Indicates whether the lead transfer operation was successful.
        data (LeadTransferResponseData): Contains detailed information about the transfer operation result.
    """

    success: bool = Field(..., description="Indicates if the transfer was successful")
    data: LeadTransferResponseData
