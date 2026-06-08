from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import APIError

from app.exceptions.ai_exceptions import AIProviderError
from app.exceptions.user_exceptions import UserAlreadyExistsError, InvalidCredentialsError


def register_exception_handlers(
        app: FastAPI,
) -> None:
    @app.exception_handler(UserAlreadyExistsError)
    async def user_already_exists_handler(
            request: Request,
            exc: UserAlreadyExistsError):
        return JSONResponse(
            status_code=409,
            content={
                "detail": str(exc)
            }
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_handler(
            request: Request,
            exc: InvalidCredentialsError):
        return JSONResponse(
            status_code=401,
            content={
                "detail": str(exc)
            }
        )

    @app.exception_handler(AIProviderError)
    async def ai_provider_handler(
            request: Request,
            exc: AIProviderError):
        return JSONResponse(
            status_code=503,
            content={
                "detail": str(exc)
            }
        )
    @app.exception_handler(APIError)
    async def ai_api_handler(
            request: Request,
            exc: APIError):
        return JSONResponse(
            status_code=503,
            content={
                "detail": "AI service temporarily unavailable"
            }
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
            request: Request,
            exc: Exception):
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error"
            }
        )
