import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.generation_service import GenerationService
from app.core.errors import GenerationError


@pytest.mark.asyncio
async def test_generate_returns_image_url():
    service = GenerationService(api_token="hf_fake")
    fake_image_bytes = b"\x89PNG\r\n"

    with patch.object(service, "_store_image", return_value="https://storage.example.com/img.png") as mock_store:
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = httpx.Response(200, content=fake_image_bytes)
            url = await service.generate("a cool prompt")

    assert url.startswith("https://")
    mock_store.assert_called_once_with(fake_image_bytes)


@pytest.mark.asyncio
async def test_generate_raises_on_api_failure():
    service = GenerationService(api_token="hf_fake")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(401, json={"error": "unauthorized"})
        with pytest.raises(GenerationError):
            await service.generate("prompt")


@pytest.mark.asyncio
async def test_generate_raises_on_503():
    service = GenerationService(api_token="hf_fake")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(503, json={"estimated_time": 20})
        with pytest.raises(GenerationError, match="loading"):
            await service.generate("prompt")
