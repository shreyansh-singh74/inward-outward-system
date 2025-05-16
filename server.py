from fastapi import FastAPI, Cookie, HTTPException, Request, BackgroundTasks
from fastapi.staticfiles import StaticFiles
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
import asyncio
from auth.utils import cleanup_expired_data

app = FastAPI()

Base.metadata.create_all(engine)

# Background task for cleanup
cleanup_task = None

@app.on_event("startup")
async def startup_event():
    global cleanup_task
    cleanup_task = asyncio.create_task(cleanup_background_task())

@app.on_event("shutdown")
async def shutdown_event():
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass

async def cleanup_background_task():
    """Run cleanup task in the background every 5 minutes"""
    while True:
        try:
            cleanup_expired_data()
        except Exception as e:
            print(f"Error in cleanup task: {str(e)}")
        await asyncio.sleep(300)  # 5 minutes


@app.get("/api/authenticate")
async def authenticate(access_token: str = Cookie(None)):
    user = protectRoute(access_token=access_token)
    if not isinstance(user, User):
        return JSONResponse(
            content={"error": "user is not authenticated"}, status_code=401
        )
    user_response = user.__dict__
    user_response.pop("_sa_instance_state", None)
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

app.mount("/assets", StaticFiles(directory="static/dist/assets"), name="assets")


@app.get("/{full_path:path}")
async def catch_all(full_path: str, request: Request):
    index_path = os.path.join("static/dist", "index.html")
    if request.url.path.startswith("/api"):
        return JSONResponse({"error": "API endpoint not found"}, status_code=404)
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "File not found"}
