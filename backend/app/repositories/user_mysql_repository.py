import aiomysql
from app.domain.repositories.user_repository import UserRepository


class UserMysqlRepository(UserRepository):
    def __init__(self, pool: aiomysql.Pool):
        self._pool = pool

    async def find_by_ids(self, ids: list[str]) -> list[dict]:
        if not ids:
            return []
        placeholders = ", ".join(["%s"] * len(ids))
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    f"SELECT id, username, avatar_url FROM users WHERE id IN ({placeholders})",
                    ids,
                )
                return await cur.fetchall()

    async def find_similar_ids(self, user_id: str, limit: int = 10) -> list[dict]:
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    """
                    SELECT u.id AS user_id, u.username, u.avatar_url,
                           COUNT(s2.style_name) AS shared_styles
                    FROM users u
                    JOIN alter_egos ae ON ae.user_id = u.id
                    JOIN alter_ego_styles s2 ON s2.alter_ego_id = ae.id
                    WHERE s2.style_name IN (
                        SELECT s1.style_name
                        FROM alter_ego_styles s1
                        JOIN alter_egos ae1 ON ae1.id = s1.alter_ego_id
                        WHERE ae1.user_id = %s
                    )
                    AND u.id != %s
                    GROUP BY u.id, u.username, u.avatar_url
                    ORDER BY shared_styles DESC
                    LIMIT %s
                    """,
                    (user_id, user_id, limit),
                )
                return await cur.fetchall()
