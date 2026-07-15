"""Authentication view schemas (request validation + response shape)."""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Incoming admin login credentials."""

    login: str = Field(min_length=1)
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    """Issued access token."""

    access_token: str
    token_type: str = "bearer"
