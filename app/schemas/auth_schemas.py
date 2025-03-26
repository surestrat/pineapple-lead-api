from pydantic import BaseModel, Field


class Token(BaseModel):
    """
    A model for representing authentication tokens.
    This model is used to structure the response when authentication is successful, containing
    both the JWT access token and the token type.
    Attributes:
        access_token (str): The JWT access token used for authentication.
        token_type (str): The type of token, typically "Bearer" for JWT tokens.
    """

    access_token: str = Field(..., description="Access token")
    token_type: str = Field(..., description="Token type (e.g., Bearer)")


class User(BaseModel):
    """
    Represents a User with username and password.
    This model is used for authentication and user management purposes.
    Attributes:
        username (str): The username of the user. Required field.
        password (str): The password of the user. Required field.
    """

    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
