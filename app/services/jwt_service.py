from datetime import datetime, UTC, timedelta

from jose import jwt, JWTError

from app.core.config import settings


class JWTService:
    def create_access_token(self, user_id: int) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)

        payload = {
            "sub": str(user_id),
            "exp": expire,
        }

        return jwt.encode(
            payload,
            settings.secret_key,
            algorithm=settings.algorithm,
        )

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                settings.secret_key,
                algorithms=settings.algorithm,
            )
        except JWTError as error:
            raise ValueError("Invalid token") from error

