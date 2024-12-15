from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from sqlalchemy import Select as select
from sqlalchemy.orm import Session
from db.models import User
from fastapi import APIRouter, status, Response, Cookie
import jwt
from config import JWT_SECRET, JWT_ALGORITHM, engine
from uuid import UUID
from db.models import UserRole
from .schema import UpdateUser
import json
from datetime import datetime

sys_admin_router = APIRouter()


@sys_admin_router.get("/get_all_user")
async def getAllUserInfo(access_token: str = Cookie(None)):
    decode = jwt.decode(access_token, JWT_SECRET, JWT_ALGORITHM)
    if not decode:
        return JSONResponse(
            content={"message": "Unauthorized request"}, status_code=401
        )
    with Session(engine) as session:
        statement = select(User).where(User.id == UUID(decode.get("sub")))
        result = session.scalars(statement).first()
        if not result:
            return JSONResponse(
                content={"message": "Unauthorized request"}, status_code=401
            )
        if not result.role == UserRole.SYSTEM_ADMIN:
            return JSONResponse(
                content={"message": "You dont't have access"}, status_code=401
            )
        statement = select(User).where(User.id != UUID(decode.get("sub")))
        result = session.scalars(statement).all()
        users = [user.__dict__ for user in result]
        for user in users:
            user.pop("_sa_instance_state", None)
            for key, value in user.items():
                if isinstance(value, UUID):
                    user[key] = str(value)
                if isinstance(value, datetime):
                    user[key] = value.isoformat()
    return JSONResponse(content={"users": users}, status_code=200)


@sys_admin_router.post("/update_user")
async def updateUserInfo(body: UpdateUser, access_token: str = Cookie(None)):
    decode = jwt.decode(access_token, JWT_SECRET, JWT_ALGORITHM)
    if not decode:
        return JSONResponse(
            content={"message": "Unauthorized request"}, status_code=401
        )
    with Session(engine) as session:
        statement = select(User).where(User.id == UUID(decode.get("sub")))
        result = session.scalars(statement).first()
        if not result:
            return JSONResponse(
                content={"message": "Unauthorized request"}, status_code=401
            )
        if not result.role == UserRole.SYSTEM_ADMIN:
            return JSONResponse(
                content={"message": "You dont't have access"}, status_code=401
            )
        statement = select(User).where(User.id != UUID(body.user_id))
        result = session.scalars(statement).first()
        if not result:
            return JSONResponse(content={"message": "User not found"}, status_code=404)
        result.department = body.department
        result.role = body.role
        session.commit()
    return JSONResponse(
        content={"message": "User info updated successfully"}, status_code=201
    )


@sys_admin_router.post("/make_admin")
async def makeSystemAdmin(access_token: str = Cookie(None)):
    decode = jwt.decode(access_token, JWT_SECRET, JWT_ALGORITHM)
    if not decode:
        return JSONResponse(
            content={"message": "Unauthorized request"}, status_code=401
        )
    with Session(engine) as session:
        statement = select(User).where(User.id == UUID(decode.get("sub")))
        result = session.scalars(statement).first()
        if not result:
            return JSONResponse(
                content={"message": "Unauthorized request"}, status_code=401
            )
        result.role = UserRole.SYSTEM_ADMIN
        session.commit()
    return JSONResponse(
        content={"message": "Now you are system admin"}, status_code=201
    )
