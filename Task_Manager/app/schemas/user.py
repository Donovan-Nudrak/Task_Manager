from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    username: str = Field(min_length=2, max_length=100, pattern=r"^[\w.-]+$")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    is_active: bool


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Claims we expect after a successful JWT decode with PyJWT-compatible `exp`."""

    model_config = ConfigDict(extra="ignore")

    sub: str
    exp: int | None = None
    iat: int | None = None
