from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.core.exception_handlers import register_exception_handlers


@pytest.fixture
def app():
    return FastAPI()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def exception_app(app):
    register_exception_handlers(app)

    return app


@pytest.fixture
def exception_client(exception_app):
    return TestClient(exception_app)


@pytest.fixture
def exception_client_no_raise(
        exception_app,
):
    return TestClient(
        exception_app,
        raise_server_exceptions=False,
    )
