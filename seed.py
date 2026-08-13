"""Seed initial users (system_admin + clerk) so the app works on a fresh database.

Usage (inside the container):
    docker compose exec web python seed.py

Idempotent: skips roles that already have a user. Emails/names come from
environment variables (set them in .env):
    SEED_ADMIN_EMAIL / SEED_ADMIN_USERNAME
    SEED_CLERK_EMAIL / SEED_CLERK_USERNAME
"""

import os

from sqlalchemy import select
from sqlalchemy.orm import Session

from config import engine
from db.models import Base, User

SEED_ROLES = [
    ("system_admin", "SEED_ADMIN_EMAIL", "SEED_ADMIN_USERNAME"),
    ("clerk", "SEED_CLERK_EMAIL", "SEED_CLERK_USERNAME"),
]

DEFAULT_DEPARTMENT = "System"


def seed() -> None:
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        for role, email_var, username_var in SEED_ROLES:
            existing = session.scalars(
                select(User).where(User.role == role)
            ).first()
            if existing:
                print(
                    f"[seed] '{role}' already exists as "
                    f"{existing.tcet_email} (skipping)"
                )
                continue

            email = os.getenv(email_var, "").strip()
            username = os.getenv(username_var, "").strip()
            if not email or not username:
                print(
                    f"[seed] Skipping '{role}': set {email_var} and "
                    f"{username_var} in .env to create it"
                )
                continue

            user = User(
                username=username,
                role=role,
                department=DEFAULT_DEPARTMENT,
                tcet_email=email,
                isEmailVerified=True,
            )
            session.add(user)
            session.commit()
            print(f"[seed] Created '{role}' user: {email}")


if __name__ == "__main__":
    seed()