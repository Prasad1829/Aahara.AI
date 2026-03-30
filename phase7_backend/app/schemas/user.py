from pydantic import BaseModel, EmailStr, Field


class UserSignup(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfileResponse(BaseModel):
    email: EmailStr
    full_name: str | None = None
    phone_number: str | None = None
    avatar_url: str | None = None
    auth_provider: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserProfileResponse | None = None


class UserProfileUpdate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    phone_number: str | None = Field(default=None, max_length=20)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=128)
