from app.domain.repositories.feed_repository import FeedRepository as FeedRepositoryABC
from app.domain.repositories.alter_ego_repository import AlterEgoRepository


class FeedRepository(FeedRepositoryABC):
    def __init__(self, pg_repo: AlterEgoRepository, driver):
        self._pg_repo = pg_repo
        self._driver = driver

    async def get_recent(self, limit: int = 20, offset: int = 0) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run(
                "MATCH (u:User)-[:CREATED]->(a:AlterEgo) "
                "RETURN a.id AS alter_ego_id "
                "SKIP $offset LIMIT $limit",
                offset=offset, limit=limit,
            )
            ids = [r["alter_ego_id"] async for r in result]

        if not ids:
            return []

        return await self._pg_repo.find_by_ids(ids)
