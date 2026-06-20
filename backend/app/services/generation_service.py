import asyncio
import httpx
from app.core.errors import GenerationError

REPLICATE_API_URL = "https://api.replicate.com/v1/predictions"
MODEL_VERSION = "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"

class GenerationService:
    def __init__(self, api_token: str):
        self._token = api_token

    async def generate(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Token {self._token}",
            "Content-Type": "application/json",
        }
        payload = {
            "version": MODEL_VERSION,
            "input": {"prompt": prompt, "width": 768, "height": 768},
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(REPLICATE_API_URL, json=payload, headers=headers)

        if response.status_code not in (200, 201):
            raise GenerationError(f"Replicate API error: {response.text}")

        prediction = response.json()
        return await self._poll_until_done(prediction["id"], headers)

    async def _poll_until_done(self, prediction_id: str, headers: dict) -> str:
        url = f"{REPLICATE_API_URL}/{prediction_id}"
        async with httpx.AsyncClient() as client:
            for _ in range(30):
                response = await client.get(url, headers=headers)
                data = response.json()
                if data["status"] == "succeeded":
                    return data["output"][0]
                if data["status"] == "failed":
                    raise GenerationError("Image generation failed")
                await asyncio.sleep(2)
        raise GenerationError("Generation timed out")
