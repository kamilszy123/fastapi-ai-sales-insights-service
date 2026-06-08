from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_user_service
from app.core.security import get_current_user
from app.exceptions.user_exceptions import UserAlreadyExistsError, InvalidCredentialsError
from app.models.user import User
from app.schemas.auth import UserResponse, RegisterRequest, TokenResponse, LoginRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
        data: RegisterRequest,
        user_service: UserService = Depends(get_user_service)
):
    return user_service.create_user(
        email=data.email,
        password=data.password,
    )


@router.post("/login", response_model=TokenResponse)
def login(
        data: LoginRequest,
        user_service: UserService = Depends(get_user_service)
):
    token = user_service.login(
        email=data.email,
        password=data.password
    )
    return TokenResponse(
        access_token=token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
def get_me(
        current_user: User = Depends(get_current_user)
):
    return current_user
