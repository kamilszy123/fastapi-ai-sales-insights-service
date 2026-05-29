from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_jwt_service
from app.models.user import User
from app.services.jwt_service import JWTService

security = HTTPBearer()

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        jwt_service: JWTService = Depends(get_jwt_service),
        db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials

    try:
        payload = jwt_service.decode_token(token)

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        user = db.get(User, int(user_id))

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found",
            )

        return user

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

