from .schema import (
    SignUpSchema,
    LoginSchema,
    ForgotPasswordSchema,
    PasswordResetConfirm,
)
import bcrypt
from sqlalchemy import Select as select
from sqlalchemy.orm import Session
from db.models import User
from fastapi import APIRouter, status, Response
from config import engine, ACCESS_TOKEN_EXPIRY, create_access_token
from datetime import timedelta
from mail import create_message
from .utils import create_url_safe_token, decode_url_safe_token
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from db.models import UserRole
from dotenv import load_dotenv

load_dotenv()
import os

authRouter = APIRouter()


@authRouter.post("/signup")
async def signup(user: SignUpSchema):
    hashedPassword = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    with Session(engine) as session:
        statement = select(User).where(User.tcet_email == user.email)
        results = session.scalars(statement).first()
        print(results)
        if results:
            return {"message": "User already exists"}
    newUser = User(
        password=hashedPassword,
        tcet_email=user.email,
        username=user.name,
        role=UserRole.STUDENT,
        department=user.department,
    )
    with Session(engine) as session:
        session.add(newUser)
        session.commit()
    token = create_url_safe_token({"email": user.email})
    link = f"http://{os.getenv("CLIENT_URL")}/verify/{token}"

    html = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """
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
            result = session.scalars(stmt).one()
            if not result:
                return {"message": "User not found"}, 401
            result.isEmailVerified = True
            session.commit()
            return JSONResponse(
                content={"message": "Account verified successfully"},
                status_code=status.HTTP_200_OK,
            )
    return JSONResponse(
        content={"message": "Invalid token"}, status_code=status.HTTP_401_UNAUTHORIZED
    )


@authRouter.post("/login")
async def login(body: LoginSchema, response: Response):
    with Session(engine) as session:
        statement = select(User).where(User.tcet_email == body.email)
        results = session.scalars(statement).first()
        if not results:
            return JSONResponse(
                content={"message": "Invalid Credentials"}, status_code=401
            )
    verifyPassword = bcrypt.checkpw(
        body.password.encode("utf-8"), results.password.encode("utf-8")
    )
    if not verifyPassword:
        return JSONResponse(content={"message": "Invalid Credentials"}, status_code=401)
    if not results.isEmailVerified:
        return JSONResponse({"message": "Email not verified"}, 401)
    access_token = create_access_token(
        data={"sub": str(results.id)},
    )
    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"},
        status_code=200,
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=3600 * 24 * 10,
        httponly=True,
        secure=False,
    )
    return response


@authRouter.post("/password-reset-request")
async def password_reset_request(email_data: ForgotPasswordSchema):
    email = email_data.email

    token = create_url_safe_token({"email": email})

    link = f"http://{os.getenv("CLIENT_URL")}/reset-password/{token}"

    html_message = f"""
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to Reset Your Password</p>
    """
    subject = "Reset Your Password"

    await create_message([email], subject, html_message)
    return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password",
        },
        status_code=status.HTTP_200_OK,
    )


@authRouter.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirm,
):
    new_password = passwords.new_password
    confirm_password = passwords.confirm_password
    if new_password != confirm_password:
        raise HTTPException(
            detail="Passwords do not match", status_code=status.HTTP_400_BAD_REQUEST
        )
    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")
    if user_email:
        with Session(engine) as session:
            stmt = select(User).where(User.tcet_email == user_email)
            result = session.scalars(stmt).first()
            print(result)
            if not result:
                return JSONResponse(
                    content={"message": "User not found"}, status_code=401
                )
            hashedPassword = bcrypt.hashpw(
                new_password.encode("utf-8"), bcrypt.gensalt()
            )
            result.password = hashedPassword
            session.commit()
        return JSONResponse(
            content={"message": "Password reset Successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during password reset."},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
