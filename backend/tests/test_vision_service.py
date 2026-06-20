import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.services.vision_service import VisionService
from app.core.errors import VisionError

MOCK_VISION_RESPONSE = {
    "responses": [{
        "faceAnnotations": [{
            "joyLikelihood": "VERY_LIKELY",
            "sorrowLikelihood": "UNLIKELY",
        }],
        "imagePropertiesAnnotation": {
            "dominantColors": {
                "colors": [{"color": {"red": 0, "green": 0, "blue": 0}, "score": 0.9}]
            }
        },
        "labelAnnotations": [
            {"description": "face", "score": 0.99},
            {"description": "hair", "score": 0.85},
        ]
    }]
}

@pytest.mark.asyncio
async def test_extract_traits_returns_dict():
    service = VisionService(api_key="fake-key")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(200, json=MOCK_VISION_RESPONSE)
        traits = await service.extract_traits("https://example.com/selfie.png")
    assert isinstance(traits, dict)
    assert "expression" in traits

@pytest.mark.asyncio
async def test_extract_traits_raises_vision_error_on_failure():
    service = VisionService(api_key="fake-key")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(400, json={"error": "bad request"})
        with pytest.raises(VisionError):
            await service.extract_traits("https://example.com/selfie.png")
