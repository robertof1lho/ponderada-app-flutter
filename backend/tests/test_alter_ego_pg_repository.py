import pytest
from unittest.mock import AsyncMock, MagicMock
from app.repositories.alter_ego_pg_repository import AlterEgoPgRepository

@pytest.fixture
def mock_client():
    client = MagicMock()
    client.table.return_value.insert.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[{
            "id": "uuid-123",
            "user_id": "user-1",
            "image_url": "https://example.com/img.png",
            "universe": "anime",
            "traits": {"expression": "smiling"},
            "created_at": "2026-06-12T00:00:00",
        }])
    )
    return client

@pytest.mark.asyncio
async def test_save_returns_alter_ego(mock_client):
    repo = AlterEgoPgRepository(client=mock_client)
    result = await repo.save(
        user_id="user-1",
        image_url="https://example.com/img.png",
        selfie_url="https://example.com/selfie.png",
        universe="anime",
        traits={"expression": "smiling"},
    )
    assert result["id"] == "uuid-123"

@pytest.mark.asyncio
async def test_find_by_ids_calls_in_filter(mock_client):
    mock_client.table.return_value.select.return_value.in_.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[])
    )
    repo = AlterEgoPgRepository(client=mock_client)
    result = await repo.find_by_ids(["uuid-123"])
    assert isinstance(result, list)
