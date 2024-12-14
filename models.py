from sqlmodel import Field, SQLModel, create_engine, Enum, Relationship
from uuid import uuid4
from datetime import datetime
from typing import List, Optional
from enum import Enum as PyEnum


class UserRole(str, PyEnum):
    STUDENT = "student"
    PRINCIPAL = "principal"
    DEPARTMENT = "department"
    EXAM_SECTION = "exam_section"
    T_AND_P = "t_and_p"
    CLERK = "clerk"


class ApplicationStatus(str, PyEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    FORWARDED = "forwarded"


class ActionType(str, PyEnum):
    INWARD = "inward"
    FORWARD = "forward"
    ACCEPT = "accept"
    REJECT = "reject"


class User(SQLModel, table=True):
    id: str = Field(default=uuid4(), primary_key=True)
    name: str = Field(max_length=200)
    role: UserRole
    department: str
    email: str = Field(max_length=200)
    tcet_email: str = Field(max_length=200)
    isEmailVerified: bool = Field(default=False)
    isAccountVerified: bool = Field(default=False)
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    applications: List["Application"] = Relationship(
        back_populates="my_application",
    )
    handled_applications: List["Application"] = Relationship(
        back_populates="current_handler"
    )


class Application(SQLModel, table=True):
    id: str = Field(default=uuid4, primary_key=True)
    user_id: str = Field(
        foreign_key="user.id",
    )
    description: str
    document_url: Optional[str] = None
    status: ApplicationStatus = Field(default=ApplicationStatus.PENDING)
    current_handler_id: Optional[str] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship(back_populates="applications")
    current_handler: User = Relationship(back_populates="handled_applications")
    actions: List["ApplicationAction"] = Relationship(back_populates="application")
    timelogs: List["TimeLog"] = Relationship(back_populates="application")


class ApplicationAction(SQLModel, table=True):
    id: Optional[str] = Field(default=uuid4, primary_key=True)
    application_id: str = Field(foreign_key="application.id")
    from_user_id: str = Field(foreign_key="user.id")
    to_user_id: str = Field(foreign_key="user.id")
    action_type: ActionType
    comments: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    application: Application = Relationship(back_populates="actions")
    from_user: User = Relationship(
        sa_relationship_kwargs={"foreign_keys": "ApplicationAction.from_user_id"}
    )
    to_user: User = Relationship(
        sa_relationship_kwargs={"foreign_keys": "ApplicationAction.to_user_id"}
    )


class Notification(SQLModel, table=True):
    id: Optional[str] = Field(default=uuid4, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    message: str
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: User = Relationship()


class TimeLog(SQLModel, table=True):
    id: Optional[int] = Field(default=uuid4, primary_key=True)
    application_id: str = Field(foreign_key="application.id")
    handler_id: str = Field(foreign_key="user.id")
    start_time: datetime
    end_time: Optional[datetime] = None
    time_exceeded: bool = Field(default=False)

    application: Application = Relationship(back_populates="timelogs")
    handler: User = Relationship()


model_config = {"arbitrary_types_allowed": True}
