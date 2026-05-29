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


@router.post("/login", response_model=TokenResponse)
def login(
        data: LoginRequest,
        user_service: UserService = Depends(get_user_service)
):
    try:
        token = user_service.login(
            email=data.email,
            password=data.password
        )
        return TokenResponse(
            access_token=token,
            token_type="bearer"
        )
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=401,
            detail=str(error),
        )

@router.get("/me", response_model=UserResponse)
def get_me(
        current_user: User = Depends(get_current_user)
):
    return current_user