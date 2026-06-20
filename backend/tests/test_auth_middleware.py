import pytest
from fastapi import HTTPException
from app.middleware.auth import verify_jwt_token


def test_missing_bearer_prefix_raises_401():
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token(authorization="not-a-bearer-token")
    assert exc_info.value.status_code == 401


def test_invalid_jwt_raises_401():
    with pytest.raises(HTTPException) as exc_info:
        verify_jwt_token(authorization="Bearer invalid.token.here")
    assert exc_info.value.status_code == 401
