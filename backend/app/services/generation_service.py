import uuid
import urllib.parse
import httpx
from app.core.errors import GenerationError

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"


class GenerationService:
    def __init__(self, api_token: str = ""):
        pass  # no token needed for Pollinations

    async def generate(self, prompt: str, negative_prompt: str = "", selfie_url: str = "") -> str:
        encoded_prompt = urllib.parse.quote(prompt)
        params = {
            "model": "flux-anime",
            "width": 768,
            "height": 768,
            "nologo": "true",
            "seed": str(uuid.uuid4().int % 2**31),
        }

        if selfie_url:
            validated = self._validate_selfie_url(selfie_url)
            if validated:
                params["image"] = validated

        url = POLLINATIONS_URL.format(prompt=encoded_prompt)

        async with httpx.AsyncClient(timeout=90, follow_redirects=True) as client:
            response = await client.get(url, params=params)

        if response.status_code != 200:
            raise GenerationError(f"Pollinations error {response.status_code}")

        content_type = response.headers.get("content-type", "image/jpeg")
        ext = ".png" if "png" in content_type else ".jpg"
        return self._store_image(response.content, ext=ext)

    def _validate_selfie_url(self, selfie_url: str) -> str | None:
        from urllib.parse import urlparse
        from app.core.config import settings

        parsed = urlparse(selfie_url)
        if parsed.scheme not in ("http", "https"):
            return None
        allowed = {urlparse(settings.minio_public_endpoint or "").netloc,
                   urlparse(settings.minio_endpoint).netloc}
        allowed.discard("")
        if parsed.netloc not in allowed:
            return None
        # Pollinations needs a publicly accessible URL — use public endpoint
        return selfie_url

    def _store_image(self, image_bytes: bytes, ext: str = ".jpg") -> str:
        from app.core.storage import get_storage_client
        from app.core.config import settings

        client = get_storage_client()
        path = f"generated/{uuid.uuid4()}{ext}"
        content_type = "image/png" if ext == ".png" else "image/jpeg"
        client.put_object(
            Bucket=settings.minio_bucket,
            Key=path,
            Body=image_bytes,
            ContentType=content_type,
        )
        return f"{settings.public_endpoint}/{settings.minio_bucket}/{path}"
