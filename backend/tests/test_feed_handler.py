import pytest
from unittest.mock import AsyncMock
from app.main import app
from app.handlers.feed_handler import _make_feed_usecase


@pytest.mark.asyncio
async def test_feed_returns_list(client, mocker):
    mock_usecase = mocker.MagicMock()
    mock_usecase.execute = AsyncMock(return_value=[])
    app.dependency_overrides[_make_feed_usecase] = lambda: mock_usecase

    response = await client.get("/feed")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert isinstance(response.json(), list)
