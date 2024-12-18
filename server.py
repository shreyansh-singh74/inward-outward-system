from fastapi import FastAPI, Cookie, HTTPException
from auth.routes import authRouter
from fastapi.responses import FileResponse
from config import engine
from db.models import Base, User
from sys_admin.routes import sys_admin_router
from applications.routes import application_router, protectRoute
from fastapi.responses import JSONResponse
from datetime import datetime
from uuid import UUID
import os

app = FastAPI()

Base.metadata.create_all(bind=engine)


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
    return JSONResponse(
        content={
            "email": user_response.get("tcet_email"),
            "id": user_response.get("id"),
            "username": user_response.get("username"),
            "role": user_response.get("role"),
            "department": user_response.get("department"),
        },
        status_code=200,
    )


@app.post("/api/logout")
def logout(access_token: str = Cookie(None)):
    user = protectRoute(access_token=access_token)
    if not isinstance(user, User):
        return JSONResponse(
            content={"error": "user is not authenticated"}, status_code=401
        )
    response = JSONResponse(content={"message": "account logged out successfully"})
    response.delete_cookie(key="access_token")
    return response


MEDIA_DIR = "media"


@app.get("/api/documents/{filename}")
async def get_document(filename: str):
    file_path = os.path.join(MEDIA_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        file_path, media_type="application/octet-stream", filename=filename
    )


app.include_router(authRouter, prefix="/api/auth")
app.include_router(sys_admin_router, prefix="/api/sys_admin")
app.include_router(application_router, prefix="/api/application")
