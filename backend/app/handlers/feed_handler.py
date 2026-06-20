from fastapi import APIRouter, Depends
from app.middleware.auth import verify_jwt_token

router = APIRouter()


@router.get("")
async def get_feed(
    limit: int = 20,
    offset: int = 0,
    claims: dict = Depends(verify_jwt_token),
):
    from app.core.db import get_pool
    import aiomysql

    user_id = claims["sub"]
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT id, image_url, universe, created_at "
                "FROM alter_egos WHERE user_id = %s "
                "ORDER BY created_at DESC LIMIT %s OFFSET %s",
                (user_id, limit, offset),
            )
            rows = await cur.fetchall()

    return [
        {
            "id": r["id"],
            "image_url": r["image_url"],
            "universe": r["universe"],
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
        }
        for r in rows
    ]
