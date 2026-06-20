import io
import httpx
import numpy as np
from PIL import Image
from app.core.errors import VisionError


class VisionService:
    def __init__(self, api_key: str = ""):
        pass  # api_key retained for interface compatibility, unused

    async def extract_traits(self, image_url: str) -> dict:
        try:
            image_bytes = await self._download(image_url)
            return self._analyze(image_bytes)
        except VisionError:
            raise
        except Exception as e:
            raise VisionError(f"Image analysis error: {e}") from e

    async def _download(self, url: str) -> bytes:
        from app.core.config import settings
        # Rewrite public MinIO URL to internal Docker hostname for container access
        if settings.minio_public_endpoint and settings.minio_public_endpoint in url:
            url = url.replace(settings.minio_public_endpoint, settings.minio_endpoint)
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url)
        if response.status_code != 200:
            raise VisionError(f"Could not download image: {response.status_code}")
        return response.content

    def _analyze(self, image_bytes: bytes) -> dict:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((64, 64))
        pixels = np.array(img)

        avg_r = float(np.mean(pixels[:, :, 0]))
        avg_g = float(np.mean(pixels[:, :, 1]))
        avg_b = float(np.mean(pixels[:, :, 2]))

        # Brightness heuristic → expression
        brightness = (avg_r + avg_g + avg_b) / 3
        expression = "smiling" if brightness > 140 else ("sad" if brightness < 80 else "neutral")

        # Dominant color channel → rough hair color estimate
        if avg_r > avg_g and avg_r > avg_b and avg_r > 150:
            hair_color = "red"
        elif avg_r < 80 and avg_g < 80 and avg_b < 80:
            hair_color = "black"
        elif avg_r > 200 and avg_g > 200:
            hair_color = "blonde"
        else:
            hair_color = "brown"

        labels = [expression, hair_color, "face"]

        return {
            "expression": expression,
            "hair_color": hair_color,
            "labels": labels,
        }
