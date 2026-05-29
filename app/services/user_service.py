from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.user_exceptions import UserAlreadyExistsError
from app.models.user import User
from app.services.auth_service import AuthService


class UserService:
    def __init__(
            self,
            db: Session,
            auth_service: AuthService,
    ) -> None:
        self.db = db
        self.auth_service = auth_service

    def create_user(
            self,
            email: str,
            password: str,
    ) -> User:

        query = select(User).where(User.email == email)
        result = self.db.execute(query)

        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise UserAlreadyExistsError("User already exists")

        user = User(
            email=email,
            hashed_password=self.auth_service.hash_password(password),
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

