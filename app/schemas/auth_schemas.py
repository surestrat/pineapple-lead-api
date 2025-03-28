from pydantic import BaseModel, Field

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class User(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=3)
