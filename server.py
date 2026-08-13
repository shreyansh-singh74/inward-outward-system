from fastapi import FastAPI, Cookie, HTTPException, Request, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from auth.routes import authRouter
from fastapi.responses import FileResponse
from config import engine
from db.models import Base, User, SupportingDocuments, Applications, UserRole, role_matches, normalize_role
from sys_admin.routes import sys_admin_router
from applications.routes import application_router, protectRoute
from fastapi.responses import JSONResponse
from datetime import datetime
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
import os
import asyncio
from auth.utils import cleanup_expired_data

from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from config import CORS_ORIGINS, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: start cleanup task
    cleanup_task = asyncio.create_task(cleanup_background_task())
    yield
    # Shutdown: cancel cleanup task
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.middleware("http")
async def no_store_api_cache(request: Request, call_next):
    """Prevent Cloudflare/browser caching of authenticated API responses."""
    response = await call_next(request)
    if request.url.path.startswith("/api"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
    return response

Base.metadata.create_all(engine)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

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
            "role": normalize_role(user_response.get("role")),
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
async def get_document(filename: str, access_token: str = Cookie(None)):
    user = protectRoute(access_token=access_token)
    if not isinstance(user, User):
        return JSONResponse(
            content={"error": "user is not authenticated"}, status_code=401
        )

    safe_filename = os.path.basename(filename)
    media_root = os.path.abspath(MEDIA_DIR)
    file_path = os.path.abspath(os.path.join(media_root, safe_filename))
    if not safe_filename or os.path.commonpath([media_root, file_path]) != media_root:
        return JSONResponse(content={"error": "Forbidden"}, status_code=403)

    # Authorization: only users linked to the application that owns the document
    with Session(engine) as session:
        statement = select(SupportingDocuments).where(
            SupportingDocuments.document_url == f"media/{safe_filename}"
        )
        document = session.scalars(statement).first()
        if not document:
            raise HTTPException(status_code=404, detail="File not found")
        statement = select(Applications).where(Applications.id == document.application_id)
        application = session.scalars(statement).first()
        if not application:
            raise HTTPException(status_code=404, detail="File not found")

        is_handler_or_creator = (
            application.created_by_id == user.id
            or application.current_handler_id == user.id
        )
        role_override = role_matches(
            user.role, UserRole.SYSTEM_ADMIN, UserRole.PRINCIPAL, UserRole.CLERK
        )
        if not (is_handler_or_creator or role_override):
            return JSONResponse(
                content={"error": "Forbidden"}, status_code=403
            )

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        file_path, media_type="application/octet-stream", filename=safe_filename
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
