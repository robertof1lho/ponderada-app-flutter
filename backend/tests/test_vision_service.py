import pytest
from unittest.mock import AsyncMock, patch
from app.services.vision_service import VisionService
from app.core.errors import VisionError
from PIL import Image
import io


def _make_image_bytes(r: int, g: int, b: int) -> bytes:
    img = Image.new("RGB", (64, 64), color=(r, g, b))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_extract_traits_bright_image_smiling():
    service = VisionService()
    bright_bytes = _make_image_bytes(200, 200, 200)
    with patch.object(service, "_download", new_callable=AsyncMock, return_value=bright_bytes):
        traits = await service.extract_traits("https://example.com/selfie.jpg")
    assert traits["expression"] == "smiling"
    assert "hair_color" in traits
    assert isinstance(traits["labels"], list)


@pytest.mark.asyncio
async def test_extract_traits_dark_image_sad():
    service = VisionService()
    dark_bytes = _make_image_bytes(50, 50, 50)
    with patch.object(service, "_download", new_callable=AsyncMock, return_value=dark_bytes):
        traits = await service.extract_traits("https://example.com/selfie.jpg")
    assert traits["expression"] == "sad"
    assert traits["hair_color"] == "black"


@pytest.mark.asyncio
async def test_extract_traits_raises_vision_error_on_download_failure():
    service = VisionService()
    with patch.object(service, "_download", new_callable=AsyncMock,
                      side_effect=VisionError("download failed")):
        with pytest.raises(VisionError):
            await service.extract_traits("https://example.com/selfie.jpg")
