import uuid
import json
import aiomysql
from app.domain.repositories.alter_ego_repository import AlterEgoRepository


class AlterEgoMysqlRepository(AlterEgoRepository):
    def __init__(self, pool: aiomysql.Pool):
        self._pool = pool

    async def save(
        self,
        user_id: str,
        image_url: str,
        selfie_url: str,
        universe: str,
        traits: dict,
        style_tags: list[str] = None,
    ) -> dict:
        alter_ego_id = str(uuid.uuid4())
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO alter_egos (id, user_id, image_url, selfie_url, universe, traits) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    (alter_ego_id, user_id, image_url, selfie_url, universe, json.dumps(traits)),
                )
                if style_tags:
                    for tag in style_tags:
                        await cur.execute(
                            "INSERT IGNORE INTO alter_ego_styles (alter_ego_id, style_name) VALUES (%s, %s)",
                            (alter_ego_id, tag),
                        )
        return {"id": alter_ego_id, "image_url": image_url}

    async def delete(self, alter_ego_id: str, user_id: str) -> bool:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "DELETE FROM alter_egos WHERE id = %s AND user_id = %s",
                    (alter_ego_id, user_id),
                )
                return cur.rowcount > 0

    async def find_by_ids(self, ids: list[str]) -> list[dict]:
        if not ids:
            return []
        placeholders = ", ".join(["%s"] * len(ids))
        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(
                    f"SELECT ae.id, ae.image_url, ae.universe, ae.created_at, u.username "
                    f"FROM alter_egos ae JOIN users u ON u.id = ae.user_id "
                    f"WHERE ae.id IN ({placeholders}) ORDER BY ae.created_at DESC",
                    ids,
                )
                return await cur.fetchall()
