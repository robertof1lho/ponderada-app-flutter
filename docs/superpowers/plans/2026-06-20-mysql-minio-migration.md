# MySQL + MinIO Migration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Supabase (Postgres + Auth + Storage) and Neo4j with MySQL (all relational data), MinIO (S3-compatible binary storage), and custom JWT auth endpoints — keeping all existing use cases and domain logic intact.

**Architecture:** All repositories are rewritten to use `aiomysql` connection pools instead of Supabase client or Neo4j driver. Graph relationships (styles, similar users) become SQL JOINs on a `alter_ego_styles` table. MinIO replaces Supabase Storage via the S3-compatible `boto3` client. A new `/auth` router provides register/login and issues HS256 JWTs, which the existing `verify_jwt_token` middleware already validates.

**Tech Stack:** FastAPI, aiomysql, boto3 (MinIO), python-jose, bcrypt, Pillow, NumPy, httpx, pytest, pytest-asyncio

## Global Constraints

- NO COMMITS during implementation
- JWT `claims["sub"]` is the authoritative user identity — never trust `user_id` from request body
- All existing use-case and domain files remain untouched unless noted
- MinIO bucket name: `alter-egos` (public) and `selfies` (private)
- MySQL charset: utf8mb4
- UUID primary keys (uuid4 strings, 36 chars)
- Python 3.11+

---

## File Map

**Create:**
- `backend/app/core/db.py` — aiomysql connection pool singleton
- `backend/app/core/storage.py` — MinIO/boto3 client singleton
- `backend/app/core/security.py` — password hashing + JWT issue/verify
- `backend/schema.sql` — MySQL DDL (run once to init DB)
- `backend/app/handlers/auth_handler.py` — POST /auth/register, POST /auth/login
- `backend/app/repositories/alter_ego_mysql_repository.py` — replaces alter_ego_pg_repository
- `backend/app/repositories/user_mysql_repository.py` — replaces user_pg_repository + user_graph_repository
- `backend/app/repositories/feed_mysql_repository.py` — replaces feed_repository
- `backend/app/repositories/like_mysql_repository.py` — replaces like_repository
- `backend/tests/test_auth_handler.py`
- `backend/tests/test_alter_ego_mysql_repository.py`
- `backend/tests/test_user_mysql_repository.py`
- `backend/tests/test_feed_mysql_repository.py`

**Modify:**
- `backend/app/core/config.py` — replace Supabase/Neo4j vars with MySQL/MinIO vars
- `backend/app/middleware/auth.py` — rename function, use `settings.jwt_secret`
- `backend/app/services/generation_service.py` — replace Supabase Storage with MinIO
- `backend/app/handlers/alter_ego_handler.py` — use MySQL repos, remove Neo4j
- `backend/app/handlers/feed_handler.py` — use MySQL feed repo
- `backend/app/handlers/profile_handler.py` — use MySQL user repo
- `backend/app/main.py` — include auth_router
- `backend/app/domain/usecases/generate_alter_ego_usecase.py` — remove graph repo dependency
- `backend/requirements.txt` — swap deps
- `backend/.env` — new env vars
- `backend/tests/conftest.py` — remove Supabase/Neo4j from client fixture

**Delete (after new files verified):**
- `backend/app/repositories/alter_ego_pg_repository.py`
- `backend/app/repositories/alter_ego_graph_repository.py`
- `backend/app/repositories/user_pg_repository.py`
- `backend/app/repositories/user_graph_repository.py`
- `backend/app/repositories/feed_repository.py`
- `backend/app/repositories/like_repository.py`

---

## Task 1: Dependencies + Config + Schema

**Files:**
- Modify: `backend/requirements.txt`
- Modify: `backend/app/core/config.py`
- Modify: `backend/.env`
- Create: `backend/schema.sql`

**Interfaces:**
- Produces: `settings.mysql_url`, `settings.minio_endpoint`, `settings.minio_access_key`, `settings.minio_secret_key`, `settings.minio_bucket`, `settings.jwt_secret`, `settings.jwt_expire_minutes`

- [ ] **Step 1: Update requirements.txt**

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
pydantic-settings==2.2.1
httpx==0.27.0
aiomysql==0.2.0
PyMySQL==1.1.1
boto3==1.34.0
python-jose[cryptography]==3.3.0
bcrypt==4.1.3
Pillow>=10.0.0
numpy>=1.26.0
pytest==8.2.0
pytest-asyncio==0.23.6
pytest-mock==3.14.0
```

- [ ] **Step 2: Update config.py**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mysql_url: str          # mysql+aiomysql://user:pass@host:3306/dbname
    minio_endpoint: str     # http://localhost:9000
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str = "alter-egos"
    jwt_secret: str
    jwt_expire_minutes: int = 60
    hf_api_token: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
```

- [ ] **Step 3: Update .env**

```
MYSQL_URL=mysql+aiomysql://root:password@localhost:3306/alterme
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=alter-egos
JWT_SECRET=change-me-in-production-use-long-random-string
JWT_EXPIRE_MINUTES=60
HF_API_TOKEN=hf_your_token_here
```

- [ ] **Step 4: Create schema.sql**

```sql
CREATE DATABASE IF NOT EXISTS alterme CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE alterme;

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alter_egos (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    selfie_url VARCHAR(500) NOT NULL,
    universe VARCHAR(50) NOT NULL,
    traits JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alter_ego_styles (
    alter_ego_id VARCHAR(36) NOT NULL,
    style_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (alter_ego_id, style_name),
    FOREIGN KEY (alter_ego_id) REFERENCES alter_egos(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS likes (
    user_id VARCHAR(36) NOT NULL,
    alter_ego_id VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, alter_ego_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (alter_ego_id) REFERENCES alter_egos(id) ON DELETE CASCADE
);
```

- [ ] **Step 5: Install new deps**

```bash
pip install aiomysql PyMySQL boto3 bcrypt
```

Expected: all install without errors.

---

## Task 2: Core Infrastructure (db pool, storage client, security)

**Files:**
- Create: `backend/app/core/db.py`
- Create: `backend/app/core/storage.py`
- Create: `backend/app/core/security.py`

**Interfaces:**
- Produces:
  - `get_pool() -> aiomysql.Pool`
  - `get_storage_client() -> boto3.client`
  - `hash_password(plain: str) -> str`
  - `verify_password(plain: str, hashed: str) -> bool`
  - `create_token(user_id: str) -> str`

- [ ] **Step 1: Create db.py**

```python
import aiomysql
from app.core.config import settings

_pool: aiomysql.Pool | None = None


async def get_pool() -> aiomysql.Pool:
    global _pool
    if _pool is None:
        # parse mysql+aiomysql://user:pass@host:port/db
        url = settings.mysql_url.replace("mysql+aiomysql://", "")
        creds, rest = url.split("@", 1)
        user, password = creds.split(":", 1)
        host_port, db = rest.split("/", 1)
        host, port = (host_port.split(":") + ["3306"])[:2]
        _pool = await aiomysql.create_pool(
            host=host, port=int(port),
            user=user, password=password,
            db=db, charset="utf8mb4",
            autocommit=True,
        )
    return _pool
```

- [ ] **Step 2: Create storage.py**

```python
import boto3
from botocore.config import Config
from app.core.config import settings

_client = None


def get_storage_client():
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            endpoint_url=settings.minio_endpoint,
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
        # ensure bucket exists
        try:
            _client.create_bucket(Bucket=settings.minio_bucket)
            _client.put_bucket_policy(
                Bucket=settings.minio_bucket,
                Policy='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":"*","Action":"s3:GetObject","Resource":"arn:aws:s3:::' + settings.minio_bucket + '/*"}]}',
            )
        except Exception:
            pass  # bucket already exists
    return _client
```

- [ ] **Step 3: Create security.py**

```python
from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt
from app.core.config import settings


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode(
        {"sub": user_id, "exp": expire},
        settings.jwt_secret,
        algorithm="HS256",
    )
```

- [ ] **Step 4: Update middleware/auth.py**

```python
from fastapi import Header, HTTPException
from jose import jwt, JWTError
from app.core.config import settings


def verify_jwt_token(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## Task 3: Auth Handler (register + login)

**Files:**
- Create: `backend/app/handlers/auth_handler.py`
- Create: `backend/tests/test_auth_handler.py`

**Interfaces:**
- Consumes: `get_pool()`, `hash_password()`, `verify_password()`, `create_token()`
- Produces: `POST /auth/register → {id, token}`, `POST /auth/login → {id, token}`

- [ ] **Step 1: Write failing test**

```python
# tests/test_auth_handler.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_register_returns_token():
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_cursor = AsyncMock()
    mock_cursor.fetchone = AsyncMock(return_value=None)
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=False)
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock(return_value=False)
    mock_conn.cursor = MagicMock(return_value=mock_cursor)
    mock_pool.acquire = MagicMock(return_value=mock_conn)

    with patch("app.handlers.auth_handler.get_pool", new=AsyncMock(return_value=mock_pool)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            resp = await c.post("/auth/register", json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "secret123",
            })
    assert resp.status_code == 201
    data = resp.json()
    assert "token" in data
    assert "id" in data


@pytest.mark.asyncio
async def test_login_returns_token():
    from app.core.security import hash_password
    hashed = hash_password("secret123")
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_cursor = AsyncMock()
    mock_cursor.fetchone = AsyncMock(return_value={"id": "user-uuid", "password_hash": hashed})
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=False)
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock(return_value=False)
    mock_conn.cursor = MagicMock(return_value=mock_cursor)
    mock_pool.acquire = MagicMock(return_value=mock_conn)

    with patch("app.handlers.auth_handler.get_pool", new=AsyncMock(return_value=mock_pool)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            resp = await c.post("/auth/login", json={
                "email": "test@example.com",
                "password": "secret123",
            })
    assert resp.status_code == 200
    assert "token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401():
    from app.core.security import hash_password
    hashed = hash_password("rightpassword")
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_cursor = AsyncMock()
    mock_cursor.fetchone = AsyncMock(return_value={"id": "user-uuid", "password_hash": hashed})
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=False)
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock(return_value=False)
    mock_conn.cursor = MagicMock(return_value=mock_cursor)
    mock_pool.acquire = MagicMock(return_value=mock_conn)

    with patch("app.handlers.auth_handler.get_pool", new=AsyncMock(return_value=mock_pool)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            resp = await c.post("/auth/login", json={
                "email": "test@example.com",
                "password": "wrongpassword",
            })
    assert resp.status_code == 401
```

- [ ] **Step 2: Create auth_handler.py**

```python
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.db import get_pool
from app.core.security import hash_password, verify_password, create_token

router = APIRouter()


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register", status_code=201)
async def register(body: RegisterRequest):
    pool = await get_pool()
    user_id = str(uuid.uuid4())
    pw_hash = hash_password(body.password)
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "INSERT INTO users (id, username, email, password_hash) VALUES (%s, %s, %s, %s)",
                (user_id, body.username, body.email, pw_hash),
            )
    return {"id": user_id, "token": create_token(user_id)}


@router.post("/login")
async def login(body: LoginRequest):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT id, password_hash FROM users WHERE email = %s",
                (body.email,),
            )
            user = await cur.fetchone()
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"id": user["id"], "token": create_token(user["id"])}
```

Add `import aiomysql` at top of auth_handler.py.

- [ ] **Step 3: Register router in main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.handlers.auth_handler import router as auth_router
from app.handlers.alter_ego_handler import router as alter_ego_router
from app.handlers.feed_handler import router as feed_router
from app.handlers.profile_handler import router as profile_router

app = FastAPI(title="AlterMe API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(alter_ego_router, prefix="/alter-ego", tags=["alter-ego"])
app.include_router(feed_router, prefix="/feed", tags=["feed"])
app.include_router(profile_router, prefix="/profile", tags=["profile"])
```

- [ ] **Step 4: Run auth tests**

```bash
cd backend && python -m pytest tests/test_auth_handler.py -v
```

Expected: 3 passed.

---

## Task 4: AlterEgo MySQL Repository

**Files:**
- Create: `backend/app/repositories/alter_ego_mysql_repository.py`
- Create: `backend/tests/test_alter_ego_mysql_repository.py`

**Interfaces:**
- Consumes: `aiomysql.Pool` from `get_pool()`
- Produces:
  - `AlterEgoMysqlRepository.save(user_id, image_url, selfie_url, universe, traits, style_tags) -> dict`
  - `AlterEgoMysqlRepository.find_by_ids(ids) -> list[dict]`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_alter_ego_mysql_repository.py
import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from app.repositories.alter_ego_mysql_repository import AlterEgoMysqlRepository


def _make_pool(fetchone_result=None, fetchall_result=None):
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_cursor = AsyncMock()
    mock_cursor.fetchone = AsyncMock(return_value=fetchone_result)
    mock_cursor.fetchall = AsyncMock(return_value=fetchall_result or [])
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=False)
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock(return_value=False)
    mock_conn.cursor = MagicMock(return_value=mock_cursor)
    mock_pool.acquire = MagicMock(return_value=mock_conn)
    return mock_pool


@pytest.mark.asyncio
async def test_save_returns_dict_with_id():
    pool = _make_pool()
    repo = AlterEgoMysqlRepository(pool)
    result = await repo.save(
        user_id="uid-1",
        image_url="http://minio/img.png",
        selfie_url="http://minio/selfie.jpg",
        universe="Anime",
        traits={"expression": "smiling"},
        style_tags=["anime", "smiling"],
    )
    assert "id" in result
    assert result["image_url"] == "http://minio/img.png"


@pytest.mark.asyncio
async def test_find_by_ids_returns_list():
    row = {
        "id": "ae-1", "image_url": "http://img", "universe": "Anime",
        "created_at": "2024-01-01", "username": "alice"
    }
    pool = _make_pool(fetchall_result=[row])
    repo = AlterEgoMysqlRepository(pool)
    result = await repo.find_by_ids(["ae-1"])
    assert len(result) == 1
    assert result[0]["id"] == "ae-1"


@pytest.mark.asyncio
async def test_find_by_ids_empty_returns_empty():
    pool = _make_pool(fetchall_result=[])
    repo = AlterEgoMysqlRepository(pool)
    result = await repo.find_by_ids([])
    assert result == []
```

- [ ] **Step 2: Create alter_ego_mysql_repository.py**

```python
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
            async with conn.cursor(aiomysql.DictCursor) as cur:
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
```

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/test_alter_ego_mysql_repository.py -v
```

Expected: 3 passed.

---

## Task 5: User + Feed + Like MySQL Repositories

**Files:**
- Create: `backend/app/repositories/user_mysql_repository.py`
- Create: `backend/app/repositories/feed_mysql_repository.py`
- Create: `backend/app/repositories/like_mysql_repository.py`
- Create: `backend/tests/test_user_mysql_repository.py`
- Create: `backend/tests/test_feed_mysql_repository.py`

**Interfaces:**
- Produces:
  - `UserMysqlRepository.find_by_ids(ids) -> list[dict]`
  - `UserMysqlRepository.find_similar_ids(user_id, limit) -> list[dict]`
  - `FeedMysqlRepository.get_recent(limit, offset) -> list[dict]`
  - `LikeMysqlRepository.save(user_id, alter_ego_id) -> None`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_user_mysql_repository.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.repositories.user_mysql_repository import UserMysqlRepository


def _pool(fetchall_result=None):
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_cursor = AsyncMock()
    mock_cursor.fetchall = AsyncMock(return_value=fetchall_result or [])
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=False)
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock(return_value=False)
    mock_conn.cursor = MagicMock(return_value=mock_cursor)
    mock_pool.acquire = MagicMock(return_value=mock_conn)
    return mock_pool


@pytest.mark.asyncio
async def test_find_by_ids_returns_users():
    pool = _pool([{"id": "u1", "username": "alice", "avatar_url": None}])
    repo = UserMysqlRepository(pool)
    result = await repo.find_by_ids(["u1"])
    assert result[0]["username"] == "alice"


@pytest.mark.asyncio
async def test_find_similar_ids_returns_list():
    pool = _pool([{"user_id": "u2", "username": "bob", "avatar_url": None, "shared_styles": 3}])
    repo = UserMysqlRepository(pool)
    result = await repo.find_similar_ids("u1", limit=5)
    assert result[0]["shared_styles"] == 3
```

```python
# tests/test_feed_mysql_repository.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.repositories.feed_mysql_repository import FeedMysqlRepository


def _pool(fetchall_result=None):
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_cursor = AsyncMock()
    mock_cursor.fetchall = AsyncMock(return_value=fetchall_result or [])
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=False)
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock(return_value=False)
    mock_conn.cursor = MagicMock(return_value=mock_cursor)
    mock_pool.acquire = MagicMock(return_value=mock_conn)
    return mock_pool


@pytest.mark.asyncio
async def test_get_recent_returns_list():
    row = {"id": "ae-1", "image_url": "http://img", "universe": "Anime",
           "created_at": "2024-01-01", "username": "alice"}
    pool = _pool([row])
    repo = FeedMysqlRepository(pool)
    result = await repo.get_recent(limit=20, offset=0)
    assert len(result) == 1
    assert result[0]["universe"] == "Anime"


@pytest.mark.asyncio
async def test_get_recent_empty_returns_empty():
    pool = _pool([])
    repo = FeedMysqlRepository(pool)
    result = await repo.get_recent(limit=20, offset=0)
    assert result == []
```

- [ ] **Step 2: Create user_mysql_repository.py**

```python
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
```

- [ ] **Step 3: Create feed_mysql_repository.py**

```python
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
```

- [ ] **Step 4: Create like_mysql_repository.py**

```python
import aiomysql
from app.domain.repositories.like_repository import LikeRepository


class LikeMysqlRepository(LikeRepository):
    def __init__(self, pool: aiomysql.Pool):
        self._pool = pool

    async def save(self, user_id: str, alter_ego_id: str) -> None:
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT IGNORE INTO likes (user_id, alter_ego_id) VALUES (%s, %s)",
                    (user_id, alter_ego_id),
                )
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests/test_user_mysql_repository.py tests/test_feed_mysql_repository.py -v
```

Expected: 4 passed.

---

## Task 6: MinIO Storage Service

**Files:**
- Modify: `backend/app/services/generation_service.py`

**Interfaces:**
- Consumes: `get_storage_client()`, `settings.minio_endpoint`, `settings.minio_bucket`
- Produces: `GenerationService.generate(prompt) -> str` (public URL to stored image)

- [ ] **Step 1: Update generation_service.py**

```python
import uuid
import httpx
from app.core.errors import GenerationError

HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"


class GenerationService:
    def __init__(self, api_token: str):
        self._token = api_token

    async def generate(self, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {self._token}"}
        payload = {
            "inputs": prompt,
            "parameters": {"width": 768, "height": 768, "num_inference_steps": 30},
        }
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(HF_API_URL, json=payload, headers=headers)
        if response.status_code == 503:
            raise GenerationError("Model is loading, try again in ~20 seconds")
        if response.status_code != 200:
            raise GenerationError(f"HF API error {response.status_code}: {response.text[:200]}")
        return self._store_image(response.content)

    def _store_image(self, image_bytes: bytes) -> str:
        from app.core.storage import get_storage_client
        from app.core.config import settings

        client = get_storage_client()
        path = f"generated/{uuid.uuid4()}.png"
        client.put_object(
            Bucket=settings.minio_bucket,
            Key=path,
            Body=image_bytes,
            ContentType="image/png",
        )
        return f"{settings.minio_endpoint}/{settings.minio_bucket}/{path}"
```

- [ ] **Step 2: Run existing generation tests**

```bash
python -m pytest tests/test_generation_service.py -v
```

Expected: all pass (tests mock the HTTP call, not the storage).

---

## Task 7: Update Handlers + UseCase

**Files:**
- Modify: `backend/app/handlers/alter_ego_handler.py`
- Modify: `backend/app/handlers/feed_handler.py`
- Modify: `backend/app/handlers/profile_handler.py`
- Modify: `backend/app/domain/usecases/generate_alter_ego_usecase.py`

**Interfaces:**
- Consumes: `get_pool()`, all MySQL repositories, `verify_jwt_token` (renamed from `verify_supabase_token`)

- [ ] **Step 1: Update generate_alter_ego_usecase.py**

Remove `alter_ego_graph_repository` — style_tags now saved directly in `alter_ego_mysql_repository.save()`.

```python
from app.services.vision_service import VisionService
from app.services.prompt_service import PromptService
from app.services.generation_service import GenerationService


class GenerateAlterEgoUseCase:
    def __init__(
        self,
        alter_ego_repository,
        vision_service: VisionService,
        prompt_service: PromptService,
        generation_service: GenerationService,
    ):
        self._repo = alter_ego_repository
        self._vision = vision_service
        self._prompt = prompt_service
        self._generation = generation_service

    async def execute(self, user_id: str, selfie_url: str, universe: str) -> dict:
        traits = await self._vision.extract_traits(selfie_url)
        prompt = self._prompt.build_prompt(traits, universe)
        image_url = await self._generation.generate(prompt)
        style_tags = self._prompt.extract_style_tags(traits, universe)
        saved = await self._repo.save(
            user_id=user_id,
            image_url=image_url,
            selfie_url=selfie_url,
            universe=universe,
            traits=traits,
            style_tags=style_tags,
        )
        return {"id": saved["id"], "image_url": image_url, "style_tags": style_tags}
```

- [ ] **Step 2: Update alter_ego_handler.py**

```python
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import GenerateAlterEgoRequest, GenerateAlterEgoResponse
from app.domain.usecases.generate_alter_ego_usecase import GenerateAlterEgoUseCase
from app.core.config import settings
from app.core.errors import VisionError, GenerationError
from app.middleware.auth import verify_jwt_token

router = APIRouter()


async def _make_generate_usecase() -> GenerateAlterEgoUseCase:
    from app.core.db import get_pool
    from app.services.vision_service import VisionService
    from app.services.prompt_service import PromptService
    from app.services.generation_service import GenerationService
    from app.repositories.alter_ego_mysql_repository import AlterEgoMysqlRepository

    pool = await get_pool()
    return GenerateAlterEgoUseCase(
        alter_ego_repository=AlterEgoMysqlRepository(pool=pool),
        vision_service=VisionService(),
        prompt_service=PromptService(),
        generation_service=GenerationService(api_token=settings.hf_api_token),
    )


async def _make_like_repository():
    from app.core.db import get_pool
    from app.repositories.like_mysql_repository import LikeMysqlRepository
    return LikeMysqlRepository(pool=await get_pool())


@router.post("/generate", response_model=GenerateAlterEgoResponse)
async def generate_alter_ego(
    body: GenerateAlterEgoRequest,
    claims: dict = Depends(verify_jwt_token),
    usecase: GenerateAlterEgoUseCase = Depends(_make_generate_usecase),
):
    try:
        result = await usecase.execute(
            user_id=claims["sub"],
            selfie_url=body.selfie_url,
            universe=body.universe,
        )
        return GenerateAlterEgoResponse(id=result["id"], image_url=result["image_url"])
    except VisionError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except GenerationError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/{alter_ego_id}/like", status_code=201)
async def like_alter_ego(
    alter_ego_id: str,
    claims: dict = Depends(verify_jwt_token),
    repo=Depends(_make_like_repository),
):
    await repo.save(user_id=claims["sub"], alter_ego_id=alter_ego_id)
    return {"ok": True}
```

- [ ] **Step 3: Update feed_handler.py**

```python
from fastapi import APIRouter, Depends
from app.domain.usecases.get_feed_usecase import GetFeedUseCase

router = APIRouter()


async def _make_feed_usecase() -> GetFeedUseCase:
    from app.core.db import get_pool
    from app.repositories.feed_mysql_repository import FeedMysqlRepository
    return GetFeedUseCase(feed_repository=FeedMysqlRepository(pool=await get_pool()))


@router.get("")
async def get_feed(
    limit: int = 20,
    offset: int = 0,
    usecase: GetFeedUseCase = Depends(_make_feed_usecase),
):
    return await usecase.execute(limit=limit, offset=offset)
```

- [ ] **Step 4: Update profile_handler.py**

```python
from fastapi import APIRouter, Depends, HTTPException
from app.domain.usecases.get_similar_users_usecase import GetSimilarUsersUseCase
from app.middleware.auth import verify_jwt_token

router = APIRouter()


async def _make_similar_users_usecase() -> GetSimilarUsersUseCase:
    from app.core.db import get_pool
    from app.repositories.user_mysql_repository import UserMysqlRepository
    return GetSimilarUsersUseCase(user_repository=UserMysqlRepository(pool=await get_pool()))


@router.get("/{user_id}/similar")
async def get_similar_users(
    user_id: str,
    limit: int = 10,
    claims: dict = Depends(verify_jwt_token),
    usecase: GetSimilarUsersUseCase = Depends(_make_similar_users_usecase),
):
    if claims["sub"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await usecase.execute(user_id=user_id, limit=limit)
```

- [ ] **Step 5: Run full test suite**

```bash
python -m pytest tests/ -q
```

Expected: all tests pass (handler tests mock repos, not DB).

---

## Task 8: Clean Up Old Files + Update Existing Tests

**Files:**
- Modify: `backend/tests/test_alter_ego_handler.py` — replace `verify_supabase_token` refs with `verify_jwt_token`
- Modify: `backend/tests/test_profile_handler.py` — same
- Modify: `backend/tests/test_auth_middleware.py` — update for new function name
- Modify: `backend/tests/test_config.py` — check new settings fields
- Modify: `backend/tests/conftest.py` — remove Supabase transport deps if any

- [ ] **Step 1: Update test_config.py**

```python
from app.core.config import settings

def test_settings_has_required_fields():
    assert hasattr(settings, "mysql_url")
    assert hasattr(settings, "minio_endpoint")
    assert hasattr(settings, "jwt_secret")
    assert hasattr(settings, "hf_api_token")
```

- [ ] **Step 2: Fix handler tests — replace mock target**

In `tests/test_alter_ego_handler.py` and `tests/test_profile_handler.py`, find all occurrences of:
```python
patch("app.middleware.auth.verify_supabase_token", ...)
```
Replace with:
```python
patch("app.middleware.auth.verify_jwt_token", ...)
```

Also update any `Depends(verify_supabase_token)` references to `Depends(verify_jwt_token)`.

- [ ] **Step 3: Update test_auth_middleware.py**

```python
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_missing_auth_header_returns_401():
    resp = client.get("/profile/some-id/similar")
    assert resp.status_code == 422  # missing Header param


def test_invalid_token_returns_401():
    resp = client.get(
        "/profile/some-id/similar",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert resp.status_code == 401
```

- [ ] **Step 4: Delete old repository files**

```bash
rm backend/app/repositories/alter_ego_pg_repository.py
rm backend/app/repositories/alter_ego_graph_repository.py
rm backend/app/repositories/user_pg_repository.py
rm backend/app/repositories/user_graph_repository.py
rm backend/app/repositories/feed_repository.py
rm backend/app/repositories/like_repository.py
```

Also delete old test files that test the removed repos:
```bash
rm backend/tests/test_alter_ego_pg_repository.py
rm backend/tests/test_alter_ego_graph_repository.py
```

- [ ] **Step 5: Final full test run**

```bash
python -m pytest tests/ -q
```

Expected: all remaining tests pass, 0 failures.

---

## Docker Compose (optional local setup reference)

To run MySQL + MinIO locally:

```yaml
# docker-compose.yml
version: "3.9"
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: alterme
    ports:
      - "3306:3306"

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
```

Then: `docker compose up -d && mysql -h 127.0.0.1 -u root -ppassword alterme < backend/schema.sql`
