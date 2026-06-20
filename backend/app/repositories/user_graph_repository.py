from app.domain.repositories.user_repository import UserRepository


class UserGraphRepository(UserRepository):
    def __init__(self, driver):
        self._driver = driver

    async def find_by_ids(self, ids: list[str]) -> list[dict]:
        raise NotImplementedError("find_by_ids is implemented by UserPgRepository")

    async def upsert(self, user_id: str) -> None:
        async with self._driver.session() as session:
            await session.run(
                "MERGE (:User {id: $id})",
                id=user_id,
            )

    async def find_similar_ids(self, user_id: str, limit: int = 10) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run(
                "MATCH (me:User {id: $uid})-[:CREATED]->(:AlterEgo)-[:HAS_STYLE]->(s:Style) "
                "<-[:HAS_STYLE]-(:AlterEgo)<-[:CREATED]-(other:User) "
                "WHERE other.id <> $uid "
                "RETURN other.id AS user_id, count(s) AS shared "
                "ORDER BY shared DESC LIMIT $limit",
                uid=user_id, limit=limit,
            )
            return [{"user_id": r["user_id"], "shared_styles": r["shared"]} async for r in result]
