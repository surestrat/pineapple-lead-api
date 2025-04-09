import uuid
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    ForeignKey,
    JSON,
    Text,
    TIMESTAMP,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.database import Base, metadata

# Update models based on the actual database schema


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    id_number = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)

    # Relationships
    quotes = relationship("Quote", back_populates="user")
    leads = relationship("Lead", back_populates="user")
    vehicles = relationship("Vehicle", back_populates="user")


class Address(Base):
    __tablename__ = "addresses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True)
    address_line = Column(String, nullable=True)
    postal_code = Column(Integer, nullable=True)
    suburb = Column(String, nullable=True)
    latitude = Column(Numeric, nullable=True)
    longitude = Column(Numeric, nullable=True)

    # Relationship
    vehicle = relationship("Vehicle", back_populates="address")
    user = relationship("User")


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True)
    marital_status = Column(String, nullable=True)
    currently_insured = Column(Boolean, nullable=True)
    years_without_claims = Column(Integer, nullable=True)
    relation_to_policy_holder = Column(String, nullable=True)
    email_address = Column(String, nullable=True)
    mobile_number = Column(String, nullable=True)
    id_number = Column(String, nullable=True)
    prv_ins_losses = Column(Integer, nullable=True)
    license_issue_date = Column(DateTime, nullable=True)  # Use DateTime for date
    date_of_birth = Column(DateTime, nullable=True)  # Use DateTime for date

    # Relationship
    vehicle = relationship("Vehicle", back_populates="driver")
    user = relationship("User")


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    external_reference_id = Column(String, nullable=True)
    source = Column(String, nullable=True)
    quote_id = Column(String, nullable=True)
    premium = Column(Numeric, nullable=True)
    excess = Column(Numeric, nullable=True)

    # Relationships
    vehicles = relationship("Vehicle", back_populates="quote")
    user = relationship("User", back_populates="quotes")
    leads = relationship("Lead", back_populates="quote")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    year = Column(Integer, nullable=True)
    make = Column(String, nullable=True)
    model = Column(String, nullable=True)
    mm_code = Column(String, nullable=True)
    modified = Column(Boolean, nullable=True)  # Changed from String to Boolean
    category = Column(String, nullable=True)
    colour = Column(String, nullable=True)
    engine_size = Column(Numeric, nullable=True)  # Changed from Float to Numeric
    financed = Column(Boolean, nullable=True)  # Changed from String to Boolean
    owner = Column(Boolean, nullable=True)  # Changed from String to Boolean
    status = Column(String, nullable=True)
    party_is_regular_driver = Column(
        Boolean, nullable=True
    )  # Changed from String to Boolean
    accessories = Column(Boolean, nullable=True)  # Changed from String to Boolean
    accessories_amount = Column(Numeric, nullable=True)  # Changed from Float to Numeric
    retail_value = Column(Numeric, nullable=True)  # Changed from Float to Numeric
    market_value = Column(Numeric, nullable=True)
    insured_value_type = Column(String, nullable=True)
    use_type = Column(String, nullable=True)
    overnight_parking_situation = Column(String, nullable=True)
    cover_code = Column(String, nullable=True)
    quote_id = Column(UUID(as_uuid=True), ForeignKey("quotes.id"), nullable=True)

    # Relationships
    address = relationship("Address", back_populates="vehicle", uselist=False)
    driver = relationship("Driver", back_populates="vehicle", uselist=False)
    quote = relationship("Quote", back_populates="vehicles")
    user = relationship("User", back_populates="vehicles")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    source = Column(String, nullable=True)
    quote_id = Column(UUID(as_uuid=True), ForeignKey("quotes.id"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="leads")
    quote = relationship("Quote", back_populates="leads")
