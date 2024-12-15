from fastapi import FastAPI, Cookie
from auth.routes import authRouter
from config import engine
from db.models import Base, User
from sys_admin.routes import sys_admin_router
from applications.routes import application_router, protectRoute
from fastapi.responses import JSONResponse
from datetime import datetime
from uuid import UUID

app = FastAPI()


@app.get("/api/authenticate")
async def authenticate(access_token: str = Cookie(None)):
    user = protectRoute(access_token=access_token)
    if not isinstance(user, User):
        return JSONResponse(
            content={"error": "user is not authenticated"}, status_code=401
        )
    user_response = user.__dict__
    user_response.pop("_sa_instance_state", None)
    print(user_response)
    for key, value in user_response.items():
        if isinstance(value, UUID):
            user_response[key] = str(value)
        if isinstance(value, datetime):
            user_response[key] = value.isoformat()
    return JSONResponse(content={"user": user}, status_code=200)


app.include_router(authRouter, prefix="/api/auth")
app.include_router(sys_admin_router, prefix="/api/sys_admin")
app.include_router(application_router, prefix="/api/application")
