from .schema import (
    SignUpSchema,
    LoginSchema,
    OTPVerificationSchema,
    ResendOTPSchema,
)
import bcrypt
from sqlalchemy import Select as select
from sqlalchemy.orm import Session
from db.models import User, VerificationToken
from fastapi import APIRouter, status, Response, Cookie, Request
from config import engine, ACCESS_TOKEN_EXPIRY, create_access_token
from datetime import timedelta
from mail import create_message
from .utils import generate_otp, store_otp, verify_otp, can_send_new_otp, store_user_registration_data, get_user_registration_data
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from db.models import UserRole
from dotenv import load_dotenv
from uuid import uuid4
from datetime import datetime, timezone

load_dotenv()
import os

authRouter = APIRouter()


@authRouter.post("/signup")
async def signup(user: SignUpSchema):
    """First step of signup - generate and send OTP"""
    # Check if user already exists
    with Session(engine) as session:
        statement = select(User).where(User.tcet_email == user.email)
        results = session.scalars(statement).first()
        if results:
            return JSONResponse(
                content={"message": "User already exists"},
                status_code=status.HTTP_400_BAD_REQUEST
            )
    
    # Check if we can send a new OTP (rate limiting)
    if not can_send_new_otp(user.email):
        return JSONResponse(
            content={"message": "Please wait before requesting a new OTP"},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    # Store user registration data temporarily
    store_user_registration_data(user.email, user.name, user.department)
    
    # Generate OTP
    otp = generate_otp()
    store_otp(user.email, otp)
    
    # Send OTP via email
    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Verification</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #ffffff; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
            <h1 style="color: #2c5282; font-size: 24px; font-weight: 600; margin-bottom: 16px;">Verify Your Email Address</h1>
            <p style="margin-bottom: 20px;">Thank you for creating an account. To complete your registration, please use the following OTP code:</p>

            <div style="background-color: #EDF2F7; padding: 16px; border-radius: 4px; text-align: center; font-size: 24px; letter-spacing: 4px; font-weight: bold; margin: 20px 0;">
                {otp}
            </div>

            <p style="margin-top: 24px; font-size: 14px; color: #666;">
                This OTP will expire in 5 minutes for security purposes. If you didn't create an account, you can safely ignore this email.
            </p>
        </div>
    </body>
    </html>"""
    
    subject = "Your OTP for Account Verification"
    emails = [user.email]
    await create_message(emails, subject, html)
    
    return JSONResponse(
        content={"message": "OTP sent to your email"},
        status_code=status.HTTP_200_OK
    )


@authRouter.post("/verify-otp/signup")
async def verify_signup_otp(verification: OTPVerificationSchema):
    """Second step of signup - verify OTP and create user"""
    # Verify the OTP
    if not verify_otp(verification.email, verification.otp):
        return JSONResponse(
            content={"message": "Invalid or expired OTP"},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Retrieve stored user registration data
    user_data = get_user_registration_data(verification.email)
    if not user_data:
        return JSONResponse(
            content={"message": "Registration session expired. Please try signing up again."},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Create the user
    newUserId = uuid4()
    newUser = User(
        id=newUserId,
        tcet_email=verification.email,
        username=user_data['name'],
        role=UserRole.STUDENT,
        department=user_data['department'],
        isEmailVerified=True  # Mark as verified immediately
    )
    
    # Save to database
    with Session(engine) as session:
        statement = select(User).where(User.tcet_email == verification.email)
        existing_user = session.scalars(statement).first()
        
        if existing_user:
            return JSONResponse(
                content={"message": "User already exists"},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        session.add(newUser)
        session.commit()
    
    # Create and return JWT token
    access_token = create_access_token(
        data={"sub": str(newUserId)},
    )
    
    response = JSONResponse(
        content={"message": "User created successfully"},
        status_code=status.HTTP_201_CREATED
    )
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=3600 * 24 * 10,  # 10 days
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    
    return response


@authRouter.post("/login")
async def login(body: LoginSchema):
    """First step of login - check user and send OTP"""
    with Session(engine) as session:
        statement = select(User).where(User.tcet_email == body.email)
        user = session.scalars(statement).first()
        if not user:
            return JSONResponse(
                content={"message": "Invalid Credentials"},
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.isEmailVerified:
            return JSONResponse(
                content={"message": "Email not verified"},
                status_code=status.HTTP_401_UNAUTHORIZED
            )
    
    # Check if we can send a new OTP (rate limiting)
    if not can_send_new_otp(body.email):
        return JSONResponse(
            content={"message": "Please wait before requesting a new OTP"},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    # Generate OTP
    otp = generate_otp()
    store_otp(body.email, otp)
    
    # Send OTP via email
    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login OTP</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #ffffff; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
            <h1 style="color: #2c5282; font-size: 24px; font-weight: 600; margin-bottom: 16px;">Your Login OTP</h1>
            <p style="margin-bottom: 20px;">Please use the following OTP to log in to your account:</p>

            <div style="background-color: #EDF2F7; padding: 16px; border-radius: 4px; text-align: center; font-size: 24px; letter-spacing: 4px; font-weight: bold; margin: 20px 0;">
                {otp}
            </div>

            <p style="margin-top: 24px; font-size: 14px; color: #666;">
                This OTP will expire in 5 minutes for security purposes. If you didn't request this OTP, please ignore this email.
            </p>
        </div>
    </body>
    </html>"""
    
    subject = "Your Login OTP"
    emails = [body.email]
    await create_message(emails, subject, html)
    
    return JSONResponse(
        content={"message": "OTP sent to your email"},
        status_code=status.HTTP_200_OK
    )


@authRouter.post("/verify-otp/login")
async def verify_login_otp(verification: OTPVerificationSchema):
    """Second step of login - verify OTP and issue JWT"""
    # Verify the OTP
    if not verify_otp(verification.email, verification.otp):
        return JSONResponse(
            content={"message": "Invalid or expired OTP"},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Get user from database
    with Session(engine) as session:
        statement = select(User).where(User.tcet_email == verification.email)
        user = session.scalars(statement).first()
        
        if not user:
            return JSONResponse(
                content={"message": "User not found"},
                status_code=status.HTTP_401_UNAUTHORIZED
            )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)},
    )
    
    response = JSONResponse(
        content={"message": "Login successful"},
        status_code=status.HTTP_200_OK
    )
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=3600 * 24 * 10,  # 10 days
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    
    return response


@authRouter.post("/resend-otp")
async def resend_otp(body: ResendOTPSchema):
    """Resend OTP to user's email"""
    # Check if user exists
    with Session(engine) as session:
        statement = select(User).where(User.tcet_email == body.email)
        user = session.scalars(statement).first()
        
        # For security reasons, always return success even if user doesn't exist
        if not user:
            return JSONResponse(
                content={"message": "If your email is registered, an OTP has been sent"},
                status_code=status.HTTP_200_OK
            )
    
    # Check if we can send a new OTP (rate limiting)
    if not can_send_new_otp(body.email):
        return JSONResponse(
            content={"message": "Please wait before requesting a new OTP"},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    # Generate OTP
    otp = generate_otp()
    store_otp(body.email, otp)
    
    # Send OTP via email
    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Resend OTP</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #ffffff; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
            <h1 style="color: #2c5282; font-size: 24px; font-weight: 600; margin-bottom: 16px;">Your New OTP</h1>
            <p style="margin-bottom: 20px;">Here is your new OTP code:</p>

            <div style="background-color: #EDF2F7; padding: 16px; border-radius: 4px; text-align: center; font-size: 24px; letter-spacing: 4px; font-weight: bold; margin: 20px 0;">
                {otp}
            </div>

            <p style="margin-top: 24px; font-size: 14px; color: #666;">
                This OTP will expire in 5 minutes for security purposes.
            </p>
        </div>
    </body>
    </html>"""
    
    subject = "Your New OTP"
    emails = [body.email]
    await create_message(emails, subject, html)
    
    return JSONResponse(
        content={"message": "If your email is registered, an OTP has been sent"},
        status_code=status.HTTP_200_OK
    )


@authRouter.post("/logout")
async def logout():
    """Logout user by clearing the JWT cookie"""
    response = JSONResponse(
        content={"message": "Logged out successfully"},
        status_code=status.HTTP_200_OK
    )
    
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    
    return response


# Keep this for backward compatibility, but it will be removed in future
@authRouter.post("/verify/{token}")
async def verify_user_account(token: str):
    """Legacy endpoint for backward compatibility"""
    return JSONResponse(
        content={"message": "This endpoint is deprecated. Please use the new OTP-based authentication."},
        status_code=status.HTTP_410_GONE
    )
