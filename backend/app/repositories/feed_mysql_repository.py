import aiomysql
from app.domain.repositories.feed_repository import FeedRepository


class FeedMysqlRepository(FeedRepository):
    def __init__(self, pool: aiomysql.Pool):
        self._pool = pool

    async def get_recent(self, limit: int = 20, offset: int = 0) -> list[dict]:
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    "SELECT ae.id, ae.image_url, ae.universe, ae.created_at, u.username "
                    "FROM alter_egos ae JOIN users u ON u.id = ae.user_id "
                    "ORDER BY ae.created_at DESC LIMIT %s OFFSET %s",
                    (limit, offset),
                )
                return await cur.fetchall()
