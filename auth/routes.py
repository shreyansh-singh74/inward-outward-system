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
        print(results)
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
    print(user_email)
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
    html = f"""
    <h1>Sign In Link</h1>
    <p>Please click this <a href="{link}">link</a> to Sign in your account</p>
    """
    subject = "Verify Your email"
    emails = [body.email]
    await create_message(emails, subject, html)
    response = JSONResponse(
        content={"message": "Login email is set to your email"},
        status_code=200,
    )
    return response
