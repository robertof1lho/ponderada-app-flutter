import aiomysql
from app.core.config import settings

_pool: aiomysql.Pool | None = None


async def get_pool() -> aiomysql.Pool:
    global _pool
    if _pool is None:
        url = settings.mysql_url.replace("mysql+aiomysql://", "")
        creds, rest = url.split("@", 1)
        user, password = creds.split(":", 1)
        host_port, db = rest.split("/", 1)
        parts = host_port.split(":")
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 3306
        _pool = await aiomysql.create_pool(
            host=host, port=port,
            user=user, password=password,
            db=db, charset="utf8mb4",
            autocommit=True,
        )
    return _pool
