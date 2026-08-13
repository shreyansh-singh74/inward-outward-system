import dotenv
import os
from typing import Optional
from db.models import User, Applications
from datetime import datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine

dotenv.load_dotenv()
db_url: str = os.getenv("DB_URL", "")
engine = create_engine(
    db_url,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
)
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET must be set in the environment")
JWT_ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRY = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")
PRODUCTION = os.getenv("PRODUCTION", "false").lower() == "true"
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()]
if PRODUCTION and not CORS_ORIGINS:
    raise RuntimeError("CORS_ORIGINS must be configured in production (fail closed)")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "5"))
ALLOWED_EXTENSIONS = set(os.getenv("ALLOWED_EXTENSIONS", "pdf,jpg,jpeg,png,doc,docx").split(","))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=int(ACCESS_TOKEN_EXPIRY) if ACCESS_TOKEN_EXPIRY.isdigit() else 1440))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

