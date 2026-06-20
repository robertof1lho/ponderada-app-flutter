import httpx
from app.core.errors import VisionError

VISION_URL = "https://vision.googleapis.com/v1/images:annotate"

class VisionService:
    def __init__(self, api_key: str):
        self._api_key = api_key

    async def extract_traits(self, image_url: str) -> dict:
        payload = {
            "requests": [{
                "image": {"source": {"imageUri": image_url}},
                "features": [
                    {"type": "FACE_DETECTION"},
                    {"type": "IMAGE_PROPERTIES"},
                    {"type": "LABEL_DETECTION", "maxResults": 5},
                ],
            }]
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{VISION_URL}?key={self._api_key}",
                json=payload,
            )

        if response.status_code != 200:
            raise VisionError(f"Vision API error: {response.text}")

        return self._parse_traits(response.json())

    def _parse_traits(self, data: dict) -> dict:
        response = data.get("responses", [{}])[0]
        traits = {}

        faces = response.get("faceAnnotations", [])
        if faces:
            face = faces[0]
            if face.get("joyLikelihood") in ("LIKELY", "VERY_LIKELY"):
                traits["expression"] = "smiling"
            elif face.get("sorrowLikelihood") in ("LIKELY", "VERY_LIKELY"):
                traits["expression"] = "sad"
            else:
                traits["expression"] = "neutral"

        colors = response.get("imagePropertiesAnnotation", {}).get("dominantColors", {}).get("colors", [])
        if colors:
            top = colors[0]["color"]
            r, g, b = top.get("red", 0), top.get("green", 0), top.get("blue", 0)
            if r > 150 and g < 100:
                traits["hair_color"] = "red"
            elif r < 80 and g < 80 and b < 80:
                traits["hair_color"] = "black"
            elif r > 200 and g > 200 and b > 200:
                traits["hair_color"] = "blonde"
            else:
                traits["hair_color"] = "brown"

        labels = [l["description"].lower() for l in response.get("labelAnnotations", [])]
        traits["labels"] = labels

        return traits
