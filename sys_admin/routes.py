from fastapi.responses import JSONResponse
from sqlalchemy import Select as select
from sqlalchemy.orm import Session
from db.models import User, UserRole, normalize_role, role_matches
from fastapi import APIRouter, Cookie
import jwt
from config import JWT_SECRET, JWT_ALGORITHM, engine
from uuid import UUID
from applications.routes import protectRoute
from datetime import datetime


sys_admin_router = APIRouter()


@sys_admin_router.get("/get_all_user")
async def getAllUserInfo(access_token: str = Cookie(None)):
    user = protectRoute(access_token)
    if not isinstance(user, User):
        return user
    if not role_matches(user.role, UserRole.SYSTEM_ADMIN):
        return JSONResponse(
            content={"message": "You don't have access"}, status_code=403
        )
    with Session(engine) as session:
        statement = select(User).where(User.id != user.id)
        result = session.scalars(statement).all()
        users = [u.__dict__ for u in result]
        for u in users:
            u.pop("_sa_instance_state", None)
            for key, value in u.items():
                if isinstance(value, UUID):
                    u[key] = str(value)
                if isinstance(value, datetime):
                    u[key] = value.isoformat()
    return JSONResponse(content={"users": users}, status_code=200)


@sys_admin_router.post("/update_user")
async def updateUserInfo(body: UpdateUser, access_token: str = Cookie(None)):
    user = protectRoute(access_token)
    if not isinstance(user, User):
        return user
    if not role_matches(user.role, UserRole.SYSTEM_ADMIN):
        return JSONResponse(
            content={"message": "You don't have access"}, status_code=403
        )
    with Session(engine) as session:
        statement = select(User).where(User.id == UUID(body.user_id))
        target_user = session.scalars(statement).first()
        if not target_user:
            return JSONResponse(content={"message": "User not found"}, status_code=404)
        target_user.department = body.department
        target_user.role = normalize_role(body.role)  # store canonical value
        session.commit()
    return JSONResponse(
        content={"message": "User info updated successfully"}, status_code=201
    )

