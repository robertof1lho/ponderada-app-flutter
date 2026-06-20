import pytest
from unittest.mock import AsyncMock
from app.main import app
from app.handlers.profile_handler import _make_similar_users_usecase
from app.middleware.auth import verify_jwt_token


@pytest.mark.asyncio
async def test_similar_users_returns_list(client, mocker):
    mock_usecase = mocker.MagicMock()
    mock_usecase.execute = AsyncMock(return_value=[])
    app.dependency_overrides[_make_similar_users_usecase] = lambda: mock_usecase
    app.dependency_overrides[verify_jwt_token] = lambda: {"sub": "user-1"}
    response = await client.get("/profile/user-1/similar")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_similar_users_returns_403_for_other_user(client, mocker):
    mock_usecase = mocker.MagicMock()
    mock_usecase.execute = AsyncMock(return_value=[])
    app.dependency_overrides[_make_similar_users_usecase] = lambda: mock_usecase
    app.dependency_overrides[verify_jwt_token] = lambda: {"sub": "other-user"}
    response = await client.get("/profile/user-1/similar")
    app.dependency_overrides.clear()
    assert response.status_code == 403
