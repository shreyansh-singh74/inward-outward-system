from .schema import (
    SignUpSchema,
    LoginSchema,
)
import bcrypt
from sqlalchemy import Select as select
from sqlalchemy.orm import Session
from db.models import User, VerificationToken
from fastapi import APIRouter, status, Response
from config import engine, ACCESS_TOKEN_EXPIRY, create_access_token
from datetime import timedelta
from mail import create_message
from .utils import create_url_safe_token, decode_url_safe_token
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
    with Session(engine) as session:
        statement = select(User).where(User.tcet_email == user.email)
        results = session.scalars(statement).first()
        if results:
            return {"message": "User already exists"}
    newUserId = uuid4()
    newUser = User(
        id=newUserId,
        tcet_email=user.email,
        username=user.name,
        role=UserRole.STUDENT,
        department=user.department,
    )
    token = create_url_safe_token({"email": user.email})
    newVerificationToken = VerificationToken(
        user_id=newUserId,
        token=token,
    )
    with Session(engine) as session:
        session.add(newUser)
        session.add(newVerificationToken)
        session.commit()
    link = f"http://{os.getenv("CLIENT_URL")}/verify/{token}"

    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Verification</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #ffffff; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
            <div style="margin-bottom: 24px; text-align: center;">
                <img src="/api/placeholder/120/40" alt="Company Logo" style="max-width: 120px;">
            </div>
            <h1 style="color: #2c5282; font-size: 24px; font-weight: 600; margin-bottom: 16px;">Verify Your Email Address</h1>
            <p style="margin-bottom: 20px;">Thank you for creating an account. To complete your registration, please verify your email address by clicking the button below.</p>

            <a href="{link}" style="display: inline-block; background-color: #3182ce; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 500; margin: 20px 0;">Verify Email Address</a>

            <p style="margin-top: 24px; font-size: 14px; color: #666;">
                If you didn't create an account, you can safely ignore this email. This verification link will expire in 5 minute for security purposes.
            </p>
        </div>
    </body>
    </html>"""
    subject = "Verify Your email"
    emails = [user.email]
    await create_message(emails, subject, html)
    return {"message": "User created successfully"}


@authRouter.post("/verify/{token}")
async def verify_user_account(token: str):
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")
    if user_email:
        with Session(engine) as session:
            stmt = select(User).where(User.tcet_email == user_email)
            statement = select(VerificationToken).where(
                VerificationToken.token == str(token)
            )
            result = session.scalars(stmt).first()
            if not result:
                return JSONResponse({"message": "User not found"}, 401)
            token_result = session.scalars(statement).first()
            if not token_result:
                return JSONResponse({"message": "Invalid token"}, status_code=401)
            if token_result.expiry < datetime.now(timezone.utc).replace(tzinfo=None):
                return JSONResponse({"message": "Token expired"}, status_code=401)
            result.isEmailVerified = True
            session.commit()
            response = JSONResponse(
                content={"message": "User is now Authorized"},
                status_code=status.HTTP_200_OK,
            )
            access_token = create_access_token(
                data={"sub": str(result.id)},
            )
            response.set_cookie(
                key="access_token",
                value=access_token,
                max_age=3600 * 24 * 10,
                httponly=True,
                secure=False,
            )
        return response
    return JSONResponse({"message": "Invalid token"}, 401)


@authRouter.post("/login")
async def login(body: LoginSchema, response: Response):
    with Session(engine) as session:
        statement = select(User).where(User.tcet_email == body.email)
        results = session.scalars(statement).first()
        if not results:
            return JSONResponse(
                content={"message": "Invalid Credentials"}, status_code=401
            )
    if not results.isEmailVerified:
        return JSONResponse({"message": "Email not verified"}, 401)
    token = create_url_safe_token({"email": body.email})
    newVerificationToken = VerificationToken(
        user_id=results.id,
        token=token,
    )
    with Session(engine) as session:
        session.add(newVerificationToken)
        session.commit()
    link = f"http://{os.getenv("CLIENT_URL")}/verify/{token}"
    html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Account Access</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #ffffff; border-radius: 8px; padding: 30px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
            <h1 style="color: #2c5282; font-size: 24px; font-weight: 600; margin-bottom: 16px;">Welcome Back</h1>
            <p>Thank you for using our service. To access your account, please click the secure link below.</p>

            <a href="{link}" style="display: inline-block; background-color: #3182ce; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 500; margin: 20px 0;">Sign In to Your Account</a>

            <p style="margin-top: 24px; font-size: 14px; color: #666;">
                If you did not request this sign-in link, please disregard this email. For security reasons, this link will expire in 5 minutes
            </p>
        </div>
    </body>
    </html>"""
    subject = "Verify Your email"
    emails = [body.email]
    await create_message(emails, subject, html)
    response = JSONResponse(
        content={"message": "Login email is set to your email"},
        status_code=200,
    )
    return response
