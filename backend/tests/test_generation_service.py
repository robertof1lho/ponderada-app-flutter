import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.services.generation_service import GenerationService
from app.core.errors import GenerationError

@pytest.mark.asyncio
async def test_generate_returns_image_url():
    service = GenerationService(api_token="fake-token")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(201, json={"id": "pred-123", "status": "starting"})
        with patch.object(service, "_poll_until_done", new_callable=AsyncMock) as mock_poll:
            mock_poll.return_value = "https://replicate.delivery/output/img.png"
            url = await service.generate("a cool prompt")
    assert url.startswith("https://")

@pytest.mark.asyncio
async def test_generate_raises_on_api_failure():
    service = GenerationService(api_token="fake-token")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(422, json={"detail": "invalid"})
        with pytest.raises(GenerationError):
            await service.generate("prompt")
