from .schema import SignUpSchema, LoginSchema, EmailSchema

import bcrypt
from sqlmodel import Session, select
from models import User
from fastapi import APIRouter
from config import engine, ACCESS_TOKEN_EXPIRY, create_access_token
from datetime import timedelta
from mail import create_message
from .utils import create_url_safe_token

authRouter = APIRouter()


@authRouter.post("/send_mail")
async def send_mail(emails: EmailSchema):
    email = emails.email
    html = "<h1>Welcome to the app</h1>"
    subject = "Welcome to our app"
    await create_message([email], subject, html)
    return {"message": "Email sent successfully"}


@authRouter.post("/signup")
async def signup(user: SignUpSchema):
    hashedPassword = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    with Session(engine) as session:
        statement = select(User).where(User.email == user.email)
        results = session.exec(statement).first()
        if results:
            return {"message": "User already exists"}
    newUser = User(email=user.email, password=str(hashedPassword), **user.dict())
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


@authRouter.post("/login")
async def login(body: LoginSchema):
    with Session(engine) as session:
        statement = select(User).where(User.email == body.email)
        results = session.exec(statement).first()
        if not results:
            return {"message": "Invalid Credentials"}, 401
    verifyPassword = bcrypt.checkpw(
        results.password.encode("utf-8"), body.password.encode("utf-8")
    )
    if not verifyPassword:
        return {"message": "Invalid Credentials"}, 401
    if not results.isEmailVerified:
        return {"message": "Email not verified"}, 401
    if not results.isAccountVerified:
        return {"message": "Account is not verified"}, 401
    access_token_expires = timedelta(minutes=float(ACCESS_TOKEN_EXPIRY))
    access_token = create_access_token(
        data={"sub": results.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
