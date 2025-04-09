from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional, Dict, Any
from uuid import UUID  # Import UUID type for user ID if applicable
from datetime import datetime


class UserLogin(BaseModel):
    model_config = ConfigDict(extra="forbid")  # Strict input

    email: EmailStr
    password: str


class User(BaseModel):
    # Represents a user object, often based on Supabase's Auth user
    model_config = ConfigDict(
        from_attributes=True, extra="allow"
    )  # Read from object, allow extra fields

    id: str | UUID  # Supabase ID is typically UUID, map to str if needed elsewhere
    email: Optional[EmailStr] = None
    # Include fields returned by db.auth.get_user().user that you need
    aud: Optional[str] = None
    role: Optional[str] = None
    app_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict
    )  # Default to empty dict
    user_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict
    )  # Default to empty dict
    created_at: Optional[datetime] = None
    # Add is_superuser or similar if implementing role checks based on metadata
    # is_superuser: bool = False # Example calculated field
