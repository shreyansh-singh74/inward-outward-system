from fastapi.responses import JSONResponse
from fastapi import UploadFile, File, Form
from sqlalchemy import Select as select
from sqlalchemy.orm import Session
from db.models import User
from fastapi import APIRouter, Cookie
import jwt
from config import JWT_SECRET, JWT_ALGORITHM, engine
from uuid import UUID
from db.models import UserRole, Applications, ApplicationActions
from datetime import datetime
from .schema import CreateApplicationSchema, UpdateApplicationSchema
from uuid import uuid4
from typing import Annotated

application_router = APIRouter()


def protectRoute(access_token: str):
    try:
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
            return result
    except Exception as e:
        print(e)
        return JSONResponse(
            content={"message": "Unauthorized request"}, status_code=401
        )


@application_router.post("/create")
async def createApplication(
    document: UploadFile,
    description: str = Form(...),
    role: str = Form(...),
    department: str = Form(...),
    access_token: str = Cookie(None),
):
    user = protectRoute(access_token)
    if not isinstance(user, User):
        return user
    document_url = None
    if document and document.filename:
        document_url = f"media/{document.filename}{uuid4()}"
        name, ext = document.filename.rsplit(".", 1)
        unique_filename = f"{name}_{uuid4()}.{ext}"
        document_url = f"media/{unique_filename}"
        with open(document_url, "wb") as f:
            content = await document.read()
            f.write(content)

    with Session(engine) as session:
        statement = select(User).where(
            User.role == role and User.department == department
        )
        receiver = session.scalars(statement).first()
        if not receiver:
            return JSONResponse(
                content={"message": "Receiver not found"}, status_code=404
            )
        newApplication = Applications(
            description=description,
            document_url=document_url,
            created_by_id=user.id,
            current_handler_id=receiver.id,
            id=uuid4(),
        )
        newApplicationAction = ApplicationActions(
            from_user_id=user.id,
            to_user_id=receiver.id,
            application_id=newApplication.id,
            action_type="INWARD",
        )
        session.add(newApplication)
        session.add(newApplicationAction)
        session.commit()
    return JSONResponse(content={"message": "Application created"}, status_code=200)


@application_router.get("/{application_id}")
async def getApplication(application_id: UUID, access_token: str = Cookie(None)):
    user = protectRoute(access_token)
    if not isinstance(user, User):
        return user
    with Session(engine) as session:
        statement = (
            select(Applications)
            .where(Applications.id == application_id)
            .join(ApplicationActions)
        ).where(ApplicationActions.application_id == application_id)
        actions_statement = select(ApplicationActions).where(
            ApplicationActions.application_id == application_id
        )
        actions = session.scalars(actions_statement).all()
        actions_list = [action.__dict__ for action in actions]
        for action in actions_list:
            action.pop("_sa_instance_state", None)
            for key, value in action.items():
                if isinstance(value, UUID):
                    action[key] = str(value)
                if isinstance(value, datetime):
                    action[key] = value.isoformat()
        result = session.scalars(statement).first()
        if not result:
            return JSONResponse(
                content={"message": "Application not found"}, status_code=404
            )
        application = result.__dict__
        application.pop("_sa_instance_state", None)

        for key, value in application.items():
            if isinstance(value, UUID):
                application[key] = str(value)
            if isinstance(value, datetime):
                application[key] = value.isoformat()
        application["actions"] = actions_list
        return JSONResponse(content={"application": application}, status_code=200)
    return JSONResponse(content={"message": "Application not found"}, status_code=404)


@application_router.get("/update/{application_id}")
async def update(
    application_id: UUID,
    body: CreateApplicationSchema,
    access_token: str = Cookie(None),
):
    user = protectRoute(access_token)
    if not isinstance(user, User):
        return user


@application_router.get("")
async def getAllApplications(
    access_token: str = Cookie(None),
):
    user = protectRoute(access_token)
    if not isinstance(user, User):
        return user
    with Session(engine) as session:
        applications = select(Applications).where(
            (Applications.created_by_id == user.id)
            | (Applications.current_handler_id == user.id)
        )
        result = session.scalars(applications).all()
    ans = [r.__dict__ for r in result]
    for r in ans:
        r.pop("_sa_instance_state", None)
        for key, value in r.items():
            if isinstance(value, UUID):
                r[key] = str(value)
            if isinstance(value, datetime):
                r[key] = value.isoformat()
    return JSONResponse(content={"applications": ans}, status_code=200)


@application_router.post("/forward/{application_id}")
async def ForwardApplication(
    application_id: UUID,
    body: UpdateApplicationSchema,
    access_token: str = Cookie(None),
):
    user = protectRoute(access_token)
    if not isinstance(user, User):
        return user
