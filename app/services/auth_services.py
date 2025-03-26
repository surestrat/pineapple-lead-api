from app.auth.jwt_utils import create_access_token
from datetime import timedelta
from app.schemas.auth_schemas import User, Token
from fastapi import HTTPException


async def authenticate_user(user: User) -> Token:
    """Authenticate a user and generate a JWT access token.

    Args:
        user (User): User credentials containing username and password.

    Returns:
        Token: An object containing the access token and token type.

    Raises:
        HTTPException: If authentication fails with 401 status code.
    """

    if user.username == "test" and user.password == "test":
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=timedelta(minutes=30)
        )
        return Token(access_token=access_token, token_type="bearer")
    else:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
