from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from enum import Enum as PyEnum
from datetime import datetime, timezone
from typing import List, Optional


class Base(DeclarativeBase):
    pass


class UserRole(str, PyEnum):
    STUDENT = "student"
    PRINCIPAL = "principal"
    HOD = "hod"
    EXAM_SECTION = "exam_section"
    T_AND_P = "t_and_p"
    CLERK = "clerk"
    SYSTEM_ADMIN = "system_admin"


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


class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    username: Mapped[str] = mapped_column(String(30))
    role: Mapped[UserRole] = mapped_column(String(200), default=UserRole.STUDENT)
    department: Mapped[str] = mapped_column(String(200))
    tcet_email: Mapped[str] = mapped_column(String(200))
    isEmailVerified: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    password: Mapped[str] = mapped_column(String(300))
    applications: Mapped[List["Applications"]] = relationship(
        "Applications",
        back_populates="creator",
        cascade="all, delete-orphan",
        foreign_keys="[Applications.created_by_id]",
    )
    hand_in: Mapped[List["Applications"]] = relationship(
        "Applications",
        back_populates="hand_in_application",
        cascade="all, delete-orphan",
        foreign_keys="[Applications.current_handler_id]",
    )
    sent_actions: Mapped[List["ApplicationActions"]] = relationship(
        "ApplicationActions",
        back_populates="from_user",
        foreign_keys="[ApplicationActions.from_user_id]",
    )
    received_actions: Mapped[List["ApplicationActions"]] = relationship(
        "ApplicationActions",
        back_populates="to_user",
        foreign_keys="[ApplicationActions.to_user_id]",
    )


class Applications(Base):
    __tablename__ = "applications"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    description: Mapped[str] = mapped_column(String(256))
    document_url: Mapped[Optional[str]] = mapped_column(
        String(200),
        default=None,
    )
    created_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    current_handler_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    creator: Mapped["User"] = relationship(
        "User", back_populates="applications", foreign_keys=[created_by_id]
    )
    hand_in_application: Mapped["User"] = relationship(
        "User", back_populates="hand_in", foreign_keys=[current_handler_id]
    )
    actions: Mapped[List["ApplicationActions"]] = relationship(
        "ApplicationActions", back_populates="application", cascade="all, delete-orphan"
    )
    status: Mapped[ApplicationStatus] = mapped_column(default=ApplicationStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    accept_reference_number: Mapped[Optional[str]] = mapped_column(
        String(200), default=None
    )


class ApplicationActions(Base):
    __tablename__ = "applicationActions"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    application_id: Mapped[str] = mapped_column(ForeignKey("applications.id"))
    from_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    to_user_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    application: Mapped["Applications"] = relationship(
        "Applications", back_populates="actions"
    )
    from_user: Mapped["User"] = relationship(
        "User", back_populates="sent_actions", foreign_keys=[from_user_id]
    )
    to_user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="received_actions", foreign_keys=[to_user_id]
    )
    action_type: Mapped[str] = mapped_column(String(200), default=ActionType.INWARD)
    comments: Mapped[Optional[str]] = mapped_column(String(200), default=None)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
