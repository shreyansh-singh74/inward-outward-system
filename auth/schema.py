from pydantic import BaseModel, EmailStr, Field


class SignUpSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)
    department: str = Field(..., min_length=1, max_length=200)
    email: EmailStr


class LoginSchema(BaseModel):
    email: EmailStr


class OTPVerificationSchema(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)


class ResendOTPSchema(BaseModel):
    email: EmailStr
