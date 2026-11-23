
import os
import secrets

from sqlmodel import Session, select

from app.db.models import User
from app.db.session import engine


DEV_EMAIL = "approver@enterpriseops.local"


def create_password_hash():
    secret = secrets.token_urlsafe(32).encode("utf-8")
    salt = os.urandom(16)

    digest = __import__("hashlib").scrypt(
        secret,
        salt=salt,
        n=2**14,
        r=8,
        p=1,
    )

    return f"scrypt$16384$8$1${salt.hex()}${digest.hex()}"


def main():
    with Session(engine) as session:
        existing = session.exec(
            select(User).where(User.email == DEV_EMAIL)
        ).first()

        if existing:
            print(f"Development approver already exists: {existing.id}")
            return

        user = User(
            email=DEV_EMAIL,
            full_name="Development Approver",
            role="approver",
            is_active=True,
            hashed_password=create_password_hash(),
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        print("Development approver created successfully.")
        print(f"User ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")


if __name__ == "__main__":
    main()
