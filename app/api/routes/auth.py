from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_user_service
from app.exceptions.user_exceptions import UserAlreadyExistsError
from app.schemas.auth import UserResponse, RegisterRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/auth")

@router.post("/register", response_model=UserResponse, status_code=201)
def register(
        data: RegisterRequest,
        user_service: UserService = Depends(get_user_service)
):
    try:
        return user_service.create_user(
            email=data.email,
            password=data.password,
        )

    except UserAlreadyExistsError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )