import dotenv
import os
from typing import Optional
from sqlmodel import create_engine, SQLModel
from models import User, Application, ApplicationAction, TimeLog, Notification
from datetime import datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer

dotenv.load_dotenv()
db_url: str = os.getenv("DB_URL", "")
engine = create_engine(db_url)
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRY = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "")
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROm = os.getenv("EMAIL_FROM")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
