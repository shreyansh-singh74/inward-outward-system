from pydantic import BaseModel, EmailStr, Field


class SignUpSchema(BaseModel):
    name: str
    department: str
    email: EmailStr


class LoginSchema(BaseModel):
    email: EmailStr


class OTPVerificationSchema(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)


class ResendOTPSchema(BaseModel):
    email: EmailStr
