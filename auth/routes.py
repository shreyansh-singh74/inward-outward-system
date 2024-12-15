from .schema import SignUpSchema, LoginSchema

import bcrypt
from sqlalchemy import Select as select
from sqlalchemy.orm import Session
from db.models import User
from fastapi import APIRouter, status
from config import engine, ACCESS_TOKEN_EXPIRY, create_access_token
from datetime import timedelta
from mail import create_message
from .utils import create_url_safe_token, decode_url_safe_token
from fastapi.responses import JSONResponse

authRouter = APIRouter()


@authRouter.post("/signup")
async def signup(user: SignUpSchema):
    hashedPassword = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    with Session(engine) as session:
        statement = select(User).where(User.tcet_email == User.tcet_email)
        results = session.scalars(statement).first()
        if results:
            return {"message": "User already exists"}
    newUser = User(
        password=hashedPassword,
        tcet_email=user.email,
        username=user.name,
        role=user.role,
        department=user.department,
    )
    with Session(engine) as session:
        session.add(newUser)
        session.commit()
    token = create_url_safe_token({"email": user.email})
    link = f"http://localhost:8000/api/auth/verify/{token}"

    html = f"""
    <h1>Verify your Email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>
    """
    subject = "Verify Your email"
    emails = [user.email, user.tcet_email]
    await create_message(emails, subject, html)
    return {"message": "User created successfully"}


@authRouter.get("/verify/{token}")
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
async def login(body: LoginSchema):
    with Session(engine) as session:
        statement = select(User).where(User.email == body.email)
        results = None
        if not results:
            return {"message": "Invalid Credentials"}, 401
    verifyPassword = bcrypt.checkpw(
        results.password.encode("utf-8"), body.password.encode("utf-8")
    )
    if not verifyPassword:
        return {"message": "Invalid Credentials"}, 401
    if not results.is_email_verified:
        return {"message": "Email not verified"}, 401
    if not results.is_account_verified:
        return {"message": "Account is not verified"}, 401
    access_token_expires = timedelta(minutes=float(ACCESS_TOKEN_EXPIRY))
    access_token = create_access_token(
        data={"sub": results.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
