from app.domain.repositories.user_repository import UserRepository


class GetSimilarUsersUseCase:
    def __init__(self, user_repository: UserRepository):
        self._repo = user_repository

    async def execute(self, user_id: str, limit: int = 10) -> list[dict]:
        return await self._repo.find_similar_ids(user_id=user_id, limit=limit)
