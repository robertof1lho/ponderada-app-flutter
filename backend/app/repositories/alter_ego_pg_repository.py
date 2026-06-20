from app.domain.repositories.alter_ego_repository import AlterEgoRepository


class AlterEgoPgRepository(AlterEgoRepository):
    def __init__(self, client):
        self._client = client

    async def save(self, user_id: str, image_url: str, selfie_url: str, universe: str, traits: dict) -> dict:
        result = await self._client.table("alter_egos").insert({
            "user_id": user_id,
            "image_url": image_url,
            "selfie_url": selfie_url,
            "universe": universe,
            "traits": traits,
        }).execute()
        return result.data[0]

    async def find_by_ids(self, ids: list[str]) -> list[dict]:
        result = await self._client.table("alter_egos").select(
            "id, image_url, universe, created_at, profiles(username)"
        ).in_("id", ids).execute()
        return result.data
