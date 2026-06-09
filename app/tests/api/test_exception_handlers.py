from app.exceptions.ai_exceptions import AIProviderError
from app.exceptions.user_exceptions import UserAlreadyExistsError, InvalidCredentialsError


def test_ai_provider_handler(
        exception_app,
        exception_client,
):
    @exception_app.get("/test")
    def test_route():
        raise AIProviderError("AI service unavailable")

    response = exception_client.get("/test")

    assert response.status_code == 503

    assert response.json() == {
        "detail": "AI service unavailable"
    }


def test_user_already_exists_handler(
        exception_app,
        exception_client,
):
    @exception_app.get("/test")
    def test_route():
        raise UserAlreadyExistsError(
            "User already exists"
        )

    response = exception_client.get("/test")

    assert response.status_code == 409

    assert response.json() == {
        "detail": "User already exists"
    }


def test_invalid_credentials_handler(
        exception_app,
        exception_client,
):
    @exception_app.get("/test")
    def test_route():
        raise InvalidCredentialsError(
            "Invalid email or password"
        )

    response = exception_client.get("/test")

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Invalid email or password"
    }


def test_generic_exception_handler(
        exception_app,
        exception_client_no_raise,
):
    @exception_app.get("/test")
    def test_route():
        raise Exception(
            "boom"
        )

    response = exception_client_no_raise.get("/test")

    assert response.status_code == 500

    assert response.json() == {
        "detail": "Internal server error"
    }
