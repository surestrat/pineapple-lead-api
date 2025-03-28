from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date, datetime
from enum import Enum


class VehicleCategory(str, Enum):
    """Vehicle category enumeration.
    An enumeration of vehicle categories represented by their abbreviated codes.
    Attributes:
        SUV (str): Sport Utility Vehicle.
        HB (str): Hatchback.
        SD (str): Sedan.
        CP (str): Coupe.
        SAV (str): Sports Activity Vehicle.
        DC (str): Double Cab.
        SC (str): Single Cab.
        MPV (str): Multi-Purpose Vehicle.
        CB (str): Cabriolet.
        SW (str): Station Wagon.
        XO (str): Crossover.
        HT (str): Hardtop.
        RV (str): Recreational Vehicle.
        CC (str): Compact Car.
        PV (str): Panel Van.
        BS (str): Bus.
        DS (str): Delivery Service.
    """

    SUV = "SUV"
    HB = "HB"
    SD = "SD"
    CP = "CP"
    SAV = "SAV"
    DC = "DC"
    SC = "SC"
    MPV = "MPV"
    CB = "CB"
    SW = "SW"
    XO = "XO"
    HT = "HT"
    RV = "RV"
    CC = "CC"
    PV = "PV"
    BS = "BS"
    DS = "DS"


class QuoteStatus(str, Enum):
    """
    Enumeration of possible quote status values.

    Attributes:
        NEW: The quote has just been created
        PENDING: The quote has been created but not yet processed by Pineapple API
        COMPLETED: The quote has been successfully processed by Pineapple API
        FAILED: The quote processing failed
    """

    NEW = "new"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class VehicleUseType(str, Enum):
    """
    Enumeration of vehicle use types.

    Attributes:
        PRIVATE: Personal use of the vehicle
        BUSINESS: Business use of the vehicle
        COMMERCIAL: Commercial use of the vehicle
    """

    PRIVATE = "Private"
    BUSINESS = "Business"
    COMMERCIAL = "Commercial"


class VehicleCoverCode(str, Enum):
    """
    Enumeration of insurance cover types.

    Attributes:
        COMPREHENSIVE: Full comprehensive insurance
        THIRD_PARTY: Third party only insurance
        THIRD_PARTY_FIRE_THEFT: Third party, fire and theft insurance
    """

    COMPREHENSIVE = "Comprehensive"
    THIRD_PARTY = "ThirdParty"
    THIRD_PARTY_FIRE_THEFT = "ThirdPartyFireAndTheft"


class MaritalStatus(str, Enum):
    """Enumeration of possible marital status values.
    Enum members:
        SINGLE: Represents a single person.
        MARRIED: Represents a married person.
        DIVORCED: Represents a divorced person.
        WIDOWED: Represents a widowed person.
        LIVING_TOGETHER: Represents people living together without legal marriage.
        ANNULMENT: Represents a marriage that has been legally declared null and void.
    """

    SINGLE = "Single"
    MARRIED = "Married"
    DIVORCED = "Divorced"
    WIDOWED = "Widowed"
    LIVING_TOGETHER = "LivingTogether"
    ANNULMENT = "Annulment"


class Address(BaseModel):
    """
    Address model representing a physical location.
    This class captures the details of a physical address including the address line,
    postal code, suburb, and geographic coordinates.
    Attributes:
        addressLine (str): The main address line for the vehicle's location.
        postalCode (int): Postal code for the address.
        suburb (str): Suburb where the vehicle is located.
        latitude (float): Latitude coordinate of the address.
        longitude (float): Longitude coordinate of the address.
    """

    addressLine: str = Field(
        ..., description="The main address line for the vehicle's location"
    )
    postalCode: int = Field(..., description="Postal code for the address")
    suburb: str = Field(..., description="Suburb where the vehicle is located")
    latitude: float = Field(..., description="Latitude coordinate of the address")
    longitude: float = Field(..., description="Longitude coordinate of the address")


class RegularDriver(BaseModel):
    """
    A model representing a regular driver for insurance quoting purposes.
    This class captures relevant personal and driving history information
    about an individual driver who is not necessarily the policy holder.
    Attributes:
        maritalStatus (MaritalStatus): Marital status of the driver.
        currentlyInsured (bool): Whether the driver currently has insurance.
        yearsWithoutClaims (int): Number of years the driver has gone without claims.
        relationToPolicyHolder (str): Driver's relationship to the policyholder.
        emailAddress (str): Driver's email address.
        mobileNumber (str): Driver's mobile phone number.
        idNumber (str): Driver's ZA ID number.
        prvInsLosses (int): Number of previous insurance losses.
        licenseIssueDate (date): Date the driver's license was issued.
        dateOfBirth (date): Driver's date of birth.
    """

    maritalStatus: MaritalStatus = Field(
        ..., description="Marital status of the driver"
    )
    currentlyInsured: bool = Field(
        ..., description="Whether the driver currently has insurance"
    )
    yearsWithoutClaims: int = Field(
        ..., description="Number of years the driver has gone without claims"
    )
    relationToPolicyHolder: str = Field(
        ..., description="Driver's relationship to the policyholder"
    )
    emailAddress: str = Field(..., description="Driver's email address")
    mobileNumber: str = Field(..., description="Driver's mobile phone number")
    idNumber: str = Field(..., description="Driver's ZA ID number")
    prvInsLosses: int = Field(..., description="Number of previous insurance losses")
    licenseIssueDate: date = Field(
        ..., description="Date the driver's license was issued"
    )
    dateOfBirth: date = Field(..., description="Driver's date of birth")


class Vehicle(BaseModel):
    """Represents a vehicle for insurance quoting purposes.
    This class defines all necessary attributes to identify and assess a vehicle
    for insurance coverage, including details about the vehicle itself, its value,
    usage patterns, and associated parties.
    Attributes:
        year (int): The manufacturing year of the vehicle.
        make (str): Manufacturer of the vehicle.
        model (str): The specific model of the vehicle.
        mmCode (str): Manufacturer's model code.
        modified (str): Indicates if the vehicle has been modified ('Y' for Yes, 'N' for No).
        category (VehicleCategory): Vehicle category enumeration.
        colour (str): Color of the vehicle.
        engineSize (float): Engine size in liters.
        financed (str): Whether the vehicle is financed ('Y' for Yes, 'N' for No).
        owner (str): Whether the requester is the vehicle owner ('Y' for Yes, 'N' for No).
        status (str): Vehicle status.
        partyIsRegularDriver (str): Indicates if the requester is the regular driver ('Y' for Yes, 'N' for No).
        accessories (str): Whether the vehicle has non-standard accessories installed ('Y' for Yes, 'N' for No).
        accessoriesAmount (Optional[int]): Value of installed accessories, if any.
        retailValue (int): The retail value of the vehicle.
        marketValue (int): The current market value of the vehicle.
        insuredValueType (str): Type of insured value.
        useType (str): Type of vehicle use (e.g., personal, business).
        overnightParkingSituation (str): Where the vehicle is parked overnight.
        coverCode (str): Type of insurance cover.
        address (Address): Address details where the vehicle is primarily kept.
        regularDriver (RegularDriver): Details about the person who regularly drives the vehicle.
    """

    year: int = Field(..., description="The manufacturing year of the vehicle")
    make: str = Field(..., description="Manufacturer of the vehicle")
    model: str = Field(..., description="The specific model of the vehicle")
    mmCode: str = Field(..., description="Manufacturer's model code")
    modified: str = Field(
        ...,
        description="Indicates if the vehicle has been modified ('Y' for Yes, 'N' for No)",
    )
    category: VehicleCategory = Field(..., description="Vehicle category")
    colour: str = Field(..., description="Color of the vehicle")
    engineSize: float = Field(..., description="Engine size in liters")
    financed: str = Field(
        ..., description="Whether the vehicle is financed ('Y' for Yes, 'N' for No)"
    )
    owner: str = Field(
        ...,
        description="Whether the requester is the vehicle owner ('Y' for Yes, 'N' for No)",
    )
    status: str = Field(..., description="Vehicle status")
    partyIsRegularDriver: str = Field(
        ...,
        description="Indicates if the requester is the regular driver ('Y' for Yes, 'N' for No)",
    )
    accessories: str = Field(
        ...,
        description="Whether the vehicle has non-standard accessories installed ('Y' for Yes, 'N' for No)",
    )
    accessoriesAmount: Optional[int] = Field(
        None, description="Value of installed accessories"
    )
    retailValue: int = Field(..., description="The retail value of the vehicle")
    marketValue: int = Field(..., description="The current market value of the vehicle")
    insuredValueType: str = Field(..., description="Type of insured value")
    useType: str = Field(..., description="Type of vehicle use")
    overnightParkingSituation: str = Field(
        ..., description="Where the vehicle is parked overnight"
    )
    coverCode: str = Field(..., description="Type of cover")
    address: Address = Field(..., description="Address details")
    regularDriver: RegularDriver = Field(..., description="Regular driver details")


class QuickQuoteRequest(BaseModel):
    """
    A request schema model for quick insurance quotes.
    This model represents the structure of a quick quote request, capturing
    essential details about the source, reference, and vehicles for insurance
    quotation purposes.
    Attributes:
        source (str): Identifies the source system or channel of the quote request.
        externalReferenceId (str): A unique reference identifier for tracking the quote
            through external systems.
        vehicles (List[Vehicle]): A list of vehicle objects containing details about
            the vehicle(s) for which insurance quotes are being requested.
        status (Optional[QuoteStatus]): Status of the quote processing (auto-set to PENDING if not provided)
    """

    source: str = Field(..., description="Identifies the source of the quote request")
    externalReferenceId: str = Field(
        ..., description="A unique reference ID for tracking the quote"
    )
    vehicles: List[Vehicle] = Field(
        ..., description="Contains the vehicle(s) for which a quote is being requested"
    )
    status: Optional[QuoteStatus] = Field(
        default=QuoteStatus.NEW, description="Status of the quote processing"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now, description="Timestamp when the quote was created"
    )


class QuoteDocumentModel(BaseModel):
    """
    Model matching the structure used in Appwrite for storing quotes.
    This ensures compatibility with the Appwrite database schema.

    Attributes:
        source (str): Identifies the source system or channel of the quote
        externalReferenceId (str): A unique reference identifier for tracking
        pineapple_quote_id (Optional[str]): ID returned from Pineapple's API
        premium (Optional[float]): Insurance premium amount
        excess (Optional[int]): Excess amount
        status (QuoteStatus): Status of the quote (pending, completed, failed)
        vehicles_data (str): JSON string containing all vehicles data
        vehicle_year (Optional[int]): Year of the first vehicle
        vehicle_make (Optional[str]): Make of the first vehicle
        vehicle_model (Optional[str]): Model of the first vehicle
        vehicle_category (Optional[str]): Category of the first vehicle
        vehicle_use_type (Optional[str]): Use type of the first vehicle
        vehicle_cover_code (Optional[str]): Cover code of the first vehicle
        driver_id_number (Optional[str]): ID number of the first driver
        driver_email (Optional[str]): Email of the first driver
        driver_mobile (Optional[str]): Mobile number of the first driver
    """

    source: str = Field(..., description="Source of the quote")
    externalReferenceId: str = Field(..., description="External reference ID")
    pineapple_quote_id: Optional[str] = Field(None, description="ID from Pineapple API")
    premium: Optional[float] = Field(None, description="Insurance premium amount")
    excess: Optional[int] = Field(None, description="Excess amount")
    status: QuoteStatus = Field(default=QuoteStatus.NEW, description="Quote status")
    vehicles_data: str = Field(..., description="JSON string of vehicles data")
    vehicle_year: Optional[int] = Field(None, description="Year of first vehicle")
    vehicle_make: Optional[str] = Field(None, description="Make of first vehicle")
    vehicle_model: Optional[str] = Field(None, description="Model of first vehicle")
    vehicle_category: Optional[str] = Field(
        None, description="Category of first vehicle"
    )
    vehicle_use_type: Optional[str] = Field(
        None, description="Use type of first vehicle"
    )
    vehicle_cover_code: Optional[str] = Field(
        None, description="Cover code of first vehicle"
    )
    driver_id_number: Optional[str] = Field(
        None, description="ID number of first driver"
    )
    driver_email: Optional[str] = Field(None, description="Email of first driver")
    driver_mobile: Optional[str] = Field(
        None, description="Mobile number of first driver"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now, description="Timestamp when the quote was created"
    )


class QuickQuoteResponseData(BaseModel):
    """
    Schema for quick quote response data.
    This model represents the structure of the data returned in a quick quote response,
    containing the premium and excess amounts for an insurance quote.
    Attributes:
        premium (float): Insurance premium amount.
        excess (int): Excess amount.
    """

    premium: float = Field(..., description="Insurance premium amount")
    excess: int = Field(..., description="Excess amount")


class QuickQuoteResponse(BaseModel):
    """
    Schema for quick quote response.
    This class represents the structure of a response for the quick quote feature.
    Attributes:
        success (bool): Indicates if the quote retrieval was successful.
        id (str): Unique identifier for the quote.
        data (List[QuickQuoteResponseData]): List of quote response data objects.
    """

    success: bool = Field(
        ..., description="Indicates if the quote retrieval was successful"
    )
    id: str = Field(..., description="Unique identifier for the quote")
    data: List[QuickQuoteResponseData]
