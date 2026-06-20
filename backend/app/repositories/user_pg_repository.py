from app.domain.repositories.user_repository import UserRepository


class UserPgRepository(UserRepository):
    def __init__(self, client):
        self._client = client

    async def find_by_ids(self, ids: list[str]) -> list[dict]:
        result = await self._client.table("profiles").select(
            "id, username, avatar_url"
        ).in_("id", ids).execute()
        return result.data

    async def find_similar_ids(self, user_id: str, limit: int = 10) -> list[dict]:
        raise NotImplementedError("find_similar_ids is implemented by UserGraphRepository")
