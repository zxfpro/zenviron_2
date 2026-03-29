from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class ErrorResponse(BaseModel):
    detail: str


class SendEmailCodeRequest(BaseModel):
    email: EmailStr


class RegisterWithCodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=8)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=8)
    new_password: str = Field(min_length=8, max_length=128)


class PhoneCodeRequest(BaseModel):
    phone: str = Field(min_length=8, max_length=20)


class PhoneLoginRequest(BaseModel):
    phone: str = Field(min_length=8, max_length=20)
    code: str = Field(min_length=4, max_length=8)


class UserMeResponse(BaseModel):
    id: str
    email: str | None
    phone: str | None
    is_active: bool
