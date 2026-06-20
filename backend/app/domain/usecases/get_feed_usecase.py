from app.domain.repositories.feed_repository import FeedRepository


class GetFeedUseCase:
    def __init__(self, feed_repository: FeedRepository):
        self._repo = feed_repository

    async def execute(self, limit: int = 20, offset: int = 0) -> list[dict]:
        return await self._repo.get_recent(limit=limit, offset=offset)
