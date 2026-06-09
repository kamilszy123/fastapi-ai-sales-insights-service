from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import get_current_user
from app.models.user import User


def test_get_current_user():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-token",
    )

    jwt_service = Mock()
    jwt_service.decode_token.return_value = {
        "sub": "1"
    }

    user = User(
        id=1,
        email="test@example.com",
        hashed_password="hash",
    )

    db = Mock()
    db.get.return_value = user

    result = get_current_user(
        credentials=credentials,
        jwt_service=jwt_service,
        db=db,
    )

    assert result == user

    jwt_service.decode_token.assert_called_once_with(
        "valid-token"
    )

    db.get.assert_called_once_with(
        User,
        1,
    )


def test_get_current_user_invalid_token():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="invalid-token",
    )

    jwt_service = Mock()
    jwt_service.decode_token.side_effect = ValueError()

    db = Mock()

    with pytest.raises(HTTPException) as exc:
        get_current_user(
            credentials=credentials,
            jwt_service=jwt_service,
            db=db,
        )

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token"
    jwt_service.decode_token.assert_called_once_with(
        "invalid-token"
    )
