import pytest
from unittest.mock import AsyncMock, MagicMock
from app.domain.usecases.get_feed_usecase import GetFeedUseCase
from app.domain.usecases.get_similar_users_usecase import GetSimilarUsersUseCase

@pytest.mark.asyncio
async def test_get_feed_calls_repository():
    mock_repo = MagicMock()
    mock_repo.get_recent = AsyncMock(return_value=[{"id": "1", "image_url": "https://x.com/img.png"}])
    usecase = GetFeedUseCase(feed_repository=mock_repo)
    result = await usecase.execute(limit=10, offset=0)
    mock_repo.get_recent.assert_called_once_with(limit=10, offset=0)
    assert len(result) == 1

@pytest.mark.asyncio
async def test_get_similar_users_calls_repository():
    mock_repo = MagicMock()
    mock_repo.find_similar_ids = AsyncMock(return_value=[])
    usecase = GetSimilarUsersUseCase(user_repository=mock_repo)
    result = await usecase.execute(user_id="user-1", limit=10)
    mock_repo.find_similar_ids.assert_called_once_with(user_id="user-1", limit=10)
    assert result == []
