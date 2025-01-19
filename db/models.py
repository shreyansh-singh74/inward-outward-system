from sqlalchemy import String, ForeignKey, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from uuid import UUID, uuid4
from enum import Enum as PyEnum
from datetime import datetime, timezone, timedelta
from typing import List, Optional


class Base(DeclarativeBase):
    pass


class UserRole(str, PyEnum):
    STUDENT = "student"
    PRINCIPAL = "principal"
    HOD = "hod"
    EXAM_SECTION = "exam_section"
    T_AND_P = "t_and_p"
    HOC = "hoc"
    CLERK = "clerk"
    SYSTEM_ADMIN = "system_admin"
    VICE_PRINCIPAL = "vice_principal"
    DEAN = "dean"
    ASSOCIATE_DEAN = "associate_dean"


class ApplicationStatus(str, PyEnum):
    PENDING = "pending"
    INCOMPLETE = "incomplete"
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


class VerificationToken(Base):
    __tablename__ = "verification_tokens"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    token: Mapped[str] = mapped_column(String(200))
    expiry: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc) + timedelta(minutes=10)
    )


class Applications(Base):
    __tablename__ = "applications"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    description: Mapped[str] = mapped_column(String(256))
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
    to: Mapped[str] = mapped_column(String(200))
    subject: Mapped[str] = mapped_column(String(200))
    status: Mapped[ApplicationStatus] = mapped_column(default=ApplicationStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    accept_reference_number: Mapped[Optional[str]] = mapped_column(
        String(200), default=None
    )
    is_verified: Mapped[bool] = mapped_column(default=False)
    supporting_documents: Mapped[List["SupportingDocuments"]] = relationship(
        "SupportingDocuments",
        back_populates="application",
        cascade="all, delete-orphan",
    )
    year: Mapped[int] = mapped_column()
    token_no: Mapped[int] = mapped_column()

    @staticmethod
    def get_next_counter(session: Session, year: int) -> int:
        stmt = select(func.max(Applications.token_no)).where(Applications.year == year)
        result = session.execute(stmt).scalar()
        return (result or 0) + 1

    @classmethod
    def create_with_counter(
        cls,
        session: Session,
        description: str,
        created_by_id: UUID,
        current_handler_id: UUID,
        id: UUID,
        to: str,
        subject: str,
        status: ApplicationStatus,
    ) -> "Applications":
        current_year = datetime.now().year
        next_counter = cls.get_next_counter(session, current_year)
        return cls(
            description=description,
            created_by_id=created_by_id,
            current_handler_id=current_handler_id,
            id=id,
            to=to,
            subject=subject,
            status=status,
            year=current_year,
            token_no=next_counter,
        )


class SupportingDocuments(Base):
    __tablename__ = "supporting_documents"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    document_name: Mapped[UUID] = mapped_column(String(200))
    document_url: Mapped[str] = mapped_column(String(200))
    application_id: Mapped[UUID] = mapped_column(ForeignKey("applications.id"))
    application: Mapped["Applications"] = relationship(
        "Applications", back_populates="supporting_documents"
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
