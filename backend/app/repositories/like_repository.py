from app.domain.repositories.like_repository import LikeRepository as LikeRepositoryABC


class LikeRepository(LikeRepositoryABC):
    def __init__(self, pg_client, graph_driver):
        self._pg = pg_client
        self._driver = graph_driver

    async def save(self, user_id: str, alter_ego_id: str) -> None:
        await self._pg.table("likes").upsert({
            "user_id": user_id,
            "alter_ego_id": alter_ego_id,
        }).execute()

        async with self._driver.session() as session:
            await session.run(
                "MERGE (u:User {id: $uid}) "
                "MERGE (a:AlterEgo {id: $aid}) "
                "MERGE (u)-[:LIKED]->(a)",
                uid=user_id, aid=alter_ego_id,
            )
