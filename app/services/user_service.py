from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.user_exceptions import UserAlreadyExistsError, InvalidCredentialsError
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.jwt_service import JWTService


class UserService:
    def __init__(
            self,
            db: Session,
            auth_service: AuthService,
            jwt_service: JWTService
    ) -> None:
        self.db = db
        self.auth_service = auth_service
        self.jwt_service = jwt_service

    def create_user(
            self,
            email: str,
            password: str,
    ) -> User:
        existing_user = self.get_by_email(email)

        if existing_user is not None:
            raise UserAlreadyExistsError("User already exists")

        user = User(
            email=email,
            hashed_password=self.auth_service.hash_password(password),
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def login(
            self,
            email: str,
            password: str
    ) -> str:
        user = self.get_by_email(email)

        if user is None:
            raise InvalidCredentialsError(
                "Invalid email or password"
            )
        is_valid = self.auth_service.verify_password(
            password,
            user.hashed_password,
        )
        if not is_valid:
            raise InvalidCredentialsError(
                "Invalid email or password"
            )
        return self.jwt_service.create_access_token(user.id)

    def get_by_email(
            self,
            email: str
    ) -> User | None:
        query = select(User).where(User.email == email)
        result = self.db.execute(query)

        return result.scalar_one_or_none()
