from pydantic import BaseModel, ConfigDict
from typing import Optional


class Token(BaseModel):
    model_config = ConfigDict(
        extra="allow"
    )  # Allow potential extra fields from Supabase

    access_token: str
    token_type: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    # Add other fields if Supabase session returns more


class TokenData(BaseModel):
    # Based on standard JWT claims often used by Supabase
    # Primarily used if manually decoding (less needed with db.auth.get_user)
    model_config = ConfigDict(extra="allow")

    sub: Optional[str] = None  # User ID (subject)
    email: Optional[str] = None
    role: Optional[str] = None
    aud: Optional[str] = None  # Audience
    exp: Optional[int] = None  # Expiration time
    # Add other fields from Supabase JWT payload if needed
