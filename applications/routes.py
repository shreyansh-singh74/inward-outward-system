from fastapi.responses import JSONResponse
from fastapi import UploadFile, File, Form
from sqlalchemy import Select as select
from sqlalchemy.orm import Session
from db.models import User
from fastapi import APIRouter, Cookie
import jwt
from config import JWT_SECRET, JWT_ALGORITHM, engine
from uuid import UUID
from db.models import Applications, ApplicationActions, ApplicationStatus
from datetime import datetime
from .schema import (
    UpdateApplicationSchema,
    ForwardApplicationSchema,
)
from uuid import uuid4
from typing import Annotated

from fastapi import APIRouter, Cookie, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, aliased
from sqlalchemy.future import select
from uuid import UUID
from datetime import datetime

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
        # Create aliases for the User table
        CreatedByUser = aliased(User, name="created_by")
        FromUser = aliased(User, name="from_user")
        ToUser = aliased(User, name="to_user")

        # Query the application along with its actions and related users (created_by, from_user, to_user)
        statement = (
            select(Applications, ApplicationActions, CreatedByUser, FromUser, ToUser)
            .outerjoin(
                ApplicationActions, ApplicationActions.application_id == Applications.id
            )
            .outerjoin(CreatedByUser, Applications.created_by_id == CreatedByUser.id)
            .outerjoin(FromUser, ApplicationActions.from_user_id == FromUser.id)
            .outerjoin(ToUser, ApplicationActions.to_user_id == ToUser.id)
            .where(Applications.id == application_id)
        )

        # Execute the query and group the results by application
        results = session.execute(statement).all()

        if not results:
            return JSONResponse(
                content={"message": "Application not found"}, status_code=404
            )

        # Initialize the application data
        application_data = None
        actions_list = []

        for row in results:
            application, action, created_by, from_user, to_user = row

            # Serialize application data (initialize once)
            if application_data is None:
                application_data = {
                    "id": str(application.id),
                    "status": application.status,
                    "created_at": (
                        application.created_at.isoformat()
                        if application.created_at
                        else None
                    ),
                    "current_handler_id": str(application.current_handler_id),
                    "document": (
                        application.document_url if application.document_url else None
                    ),
                    "description": (
                        application.description if application.description else None
                    ),
                    "created_by": (
                        {
                            "id": str(created_by.id) if created_by else None,
                            "username": created_by.username if created_by else None,
                            "role": created_by.role if created_by else None,
                            "department": created_by.department if created_by else None,
                            "tcet_email": created_by.tcet_email if created_by else None,
                        }
                        if created_by
                        else None
                    ),
                }

            # Serialize action data
            if action:
                actions_list.append(
                    {
                        "id": str(action.id),
                        "action_type": action.action_type,
                        "comment": action.comments,
                        "created_at": (
                            action.created_at.isoformat() if action.created_at else None
                        ),
                        "from_user": (
                            {
                                "id": str(from_user.id) if from_user else None,
                                "username": from_user.username if from_user else None,
                            }
                            if from_user
                            else None
                        ),
                        "to_user": (
                            {
                                "id": str(to_user.id) if to_user else None,
                                "name": to_user.username if to_user else None,
                            }
                            if to_user
                            else None
                        ),
                    }
                )

        # Add actions to the application data
        if application_data:
            application_data["actions"] = actions_list

        return JSONResponse(content={"application": application_data}, status_code=200)

    return JSONResponse(content={"message": "Application not found"}, status_code=404)


@application_router.post("/update/{application_id}")
async def update(
    application_id: UUID,
    body: UpdateApplicationSchema,
    access_token: str = Cookie(None),
):
    user = protectRoute(access_token)
    if not isinstance(user, User):
        return user
    with Session(engine) as session:
        statement = select(Applications).where(Applications.id == application_id)
        result = session.scalars(statement).first()
        if not result:
            return JSONResponse(
                content={"message": "Application not found"}, status_code=404
            )
        if result.current_handler_id != user.id:
            return JSONResponse(
                content={"message": "You dont't have access"}, status_code=401
            )
        result.status = ApplicationStatus[body.status]
        newApplicationAction = ApplicationActions(
            from_user_id=user.id,
            to_user_id=result.created_by_id,
            application_id=result.id,
            action_type=body.status,
            comments=body.remark,
        )
        session.add(newApplicationAction)
        session.commit()
    return JSONResponse(content={"message": "Application updated"}, status_code=200)


@application_router.post("/all")
async def getAllApplications(
    access_token: str = Cookie(None),
):
    user = protectRoute(access_token)
    if not isinstance(user, User):
        return user
    print("here")
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
    print(ans)
    return JSONResponse(content={"applications": ans}, status_code=200)


@application_router.post("/forward/{application_id}")
async def ForwardApplication(
    application_id: UUID,
    body: ForwardApplicationSchema,
    access_token: str = Cookie(None),
):
    user = protectRoute(access_token)
    if not isinstance(user, User):
        return user
    with Session(engine) as session:
        statement = select(Applications).where(Applications.id == application_id)
        result = session.scalars(statement).first()
        if not result:
            return JSONResponse(
                content={"message": "Application not found"}, status_code=404
            )
        if result.current_handler_id != user.id:
            return JSONResponse(
                content={"message": "You dont't have access"}, status_code=401
            )
        statement = select(User).where(
            User.role == body.role and User.department == body.department
        )
        receiver = session.scalars(statement).first()
        if not receiver:
            return JSONResponse(
                content={"message": "Receiver not found"}, status_code=404
            )
        result.current_handler_id = receiver.id
        result.status = ApplicationStatus.FORWARDED
        newApplicationAction = ApplicationActions(
            from_user_id=user.id,
            to_user_id=receiver.id,
            application_id=result.id,
            action_type="FORWARD",
            comments=body.remark,
        )
        session.add(newApplicationAction)
        session.commit()
    return JSONResponse(content={"message": "Application forwarded"}, status_code=200)
