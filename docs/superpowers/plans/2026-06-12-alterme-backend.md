# AlterMe Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a FastAPI backend with handlers/services/repositories that orquestra Google Vision API + Replicate API, persists data in Supabase Postgres and Neo4j Aura, and serves the AlterMe Flutter app.

**Architecture:** Handlers validate HTTP requests and delegate to services (external APIs) and repositories (databases). A `domain/` layer defines abstract repository interfaces (ABCs) and use case classes — concrete implementations in `repositories/` implement these ABCs. Handlers receive repository interfaces via FastAPI `Depends`. Postgres stores rich entity data; Neo4j stores only IDs and relationships. The feed_repository joins both.

**Tech Stack:** FastAPI, Pydantic v2, asyncpg (via supabase-py), neo4j Python driver, httpx, pytest, pytest-asyncio

---

## File Map

| File | Responsibility |
|------|---------------|
| `app/main.py` | FastAPI instance, routers, CORS |
| `app/core/config.py` | Pydantic Settings from .env |
| `app/core/errors.py` | Typed exceptions: VisionError, GenerationError, Neo4jError, NotFoundError |
| `app/models/schemas.py` | All Pydantic request/response models |
| `app/domain/repositories/alter_ego_repository.py` | ABC: save(), find_by_ids() |
| `app/domain/repositories/user_repository.py` | ABC: find_by_ids(), find_similar_ids() |
| `app/domain/repositories/feed_repository.py` | ABC: get_recent() |
| `app/domain/repositories/like_repository.py` | ABC: save() |
| `app/domain/usecases/generate_alter_ego_usecase.py` | Orchestrates vision → prompt → generation → save |
| `app/domain/usecases/get_feed_usecase.py` | Calls feed_repository.get_recent() |
| `app/domain/usecases/get_similar_users_usecase.py` | Calls user_repository.find_similar_ids() + find_by_ids() |
| `app/repositories/alter_ego_pg_repository.py` | Implements AlterEgoRepository: Postgres CRUD |
| `app/repositories/alter_ego_graph_repository.py` | Implements AlterEgoRepository (graph side): Neo4j AlterEgo node + HAS_STYLE edges |
| `app/repositories/user_pg_repository.py` | Implements UserRepository (pg side): Postgres SELECT profiles |
| `app/repositories/user_graph_repository.py` | Implements UserRepository (graph side): Neo4j User node + similarity query |
| `app/repositories/like_repository.py` | Implements LikeRepository: Postgres likes + Neo4j LIKED edge |
| `app/repositories/feed_repository.py` | Implements FeedRepository: Neo4j IDs → Postgres join |
| `app/services/vision_service.py` | Google Vision API: extract traits from image URL |
| `app/services/prompt_service.py` | Build Replicate prompt from traits + universe |
| `app/services/generation_service.py` | Replicate API: generate image from prompt |
| `app/handlers/alter_ego_handler.py` | POST /alter-ego/generate, POST /alter-ego/{id}/like |
| `app/handlers/feed_handler.py` | GET /feed |
| `app/handlers/profile_handler.py` | GET /profile/{user_id}/similar |
| `app/middleware/auth.py` | Validate Supabase JWT on protected routes |
| `tests/conftest.py` | pytest fixtures: test client, mock services |
| `tests/test_alter_ego_handler.py` | Handler integration tests |
| `tests/test_feed_handler.py` | Handler integration tests |
| `tests/test_profile_handler.py` | Handler integration tests |
| `tests/test_vision_service.py` | Unit tests with mocked httpx |
| `tests/test_prompt_service.py` | Unit tests |
| `tests/test_generation_service.py` | Unit tests with mocked httpx |

---

## Task 1: Project Scaffolding

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/.env.example`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`

- [ ] **Step 1: Create backend directory and requirements**

```
backend/
├── app/
│   ├── __init__.py
│   ├── core/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── handlers/
│   └── middleware/
└── tests/
```

Run:
```bash
mkdir -p backend/app/core backend/app/models backend/app/repositories
mkdir -p backend/app/services backend/app/handlers backend/app/middleware
mkdir -p backend/tests
touch backend/app/__init__.py backend/app/core/__init__.py
touch backend/app/models/__init__.py backend/app/repositories/__init__.py
touch backend/app/services/__init__.py backend/app/handlers/__init__.py
touch backend/app/middleware/__init__.py backend/tests/__init__.py
```

- [ ] **Step 2: Write requirements.txt**

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
pydantic-settings==2.2.1
httpx==0.27.0
neo4j==5.20.0
supabase==2.4.3
python-jose[cryptography]==3.3.0
pytest==8.2.0
pytest-asyncio==0.23.6
pytest-mock==3.14.0
```

- [ ] **Step 3: Write .env.example**

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
GOOGLE_VISION_API_KEY=your-key
REPLICATE_API_TOKEN=your-token
```

- [ ] **Step 4: Write app/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app.include_router(alter_ego_router, prefix="/alter-ego", tags=["alter-ego"])
app.include_router(feed_router, prefix="/feed", tags=["feed"])
app.include_router(profile_router, prefix="/profile", tags=["profile"])
```

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "feat: scaffold backend FastAPI project"
```

---

## Task 2: Core Config and Errors

**Files:**
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/errors.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_config.py
from app.core.config import settings

def test_settings_has_required_fields():
    assert hasattr(settings, "supabase_url")
    assert hasattr(settings, "neo4j_uri")
    assert hasattr(settings, "google_vision_api_key")
    assert hasattr(settings, "replicate_api_token")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend && python -m pytest tests/test_config.py -v
```
Expected: `ModuleNotFoundError` or `ImportError`

- [ ] **Step 3: Write app/core/config.py**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    supabase_url: str
    supabase_service_role_key: str
    supabase_jwt_secret: str
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    google_vision_api_key: str
    replicate_api_token: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
```

- [ ] **Step 4: Write app/core/errors.py**

```python
class AlterMeError(Exception):
    pass

class VisionError(AlterMeError):
    pass

class GenerationError(AlterMeError):
    pass

class Neo4jError(AlterMeError):
    pass

class NotFoundError(AlterMeError):
    pass
```

- [ ] **Step 5: Run test to verify it passes**

```bash
python -m pytest tests/test_config.py -v
```
Expected: PASS (requires .env file with values)

- [ ] **Step 6: Commit**

```bash
git add backend/app/core/
git commit -m "feat: add core config and typed errors"
```

---

## Task 3: Pydantic Schemas

**Files:**
- Create: `backend/app/models/schemas.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_schemas.py
from app.models.schemas import GenerateAlterEgoRequest, AlterEgoResponse, FeedItem

def test_generate_request_requires_fields():
    from pydantic import ValidationError
    import pytest
    with pytest.raises(ValidationError):
        GenerateAlterEgoRequest()

def test_alter_ego_response_has_image_url():
    r = AlterEgoResponse(id="abc", image_url="https://example.com/img.png", universe="anime")
    assert r.image_url == "https://example.com/img.png"
```

- [ ] **Step 2: Run to verify it fails**

```bash
python -m pytest tests/test_schemas.py -v
```

- [ ] **Step 3: Write app/models/schemas.py**

```python
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class GenerateAlterEgoRequest(BaseModel):
    selfie_url: str
    universe: str
    user_id: str

class LikeRequest(BaseModel):
    user_id: str

class AlterEgoResponse(BaseModel):
    id: str
    image_url: str
    universe: str
    created_at: Optional[datetime] = None
    username: Optional[str] = None

class FeedItem(BaseModel):
    alter_ego_id: str
    image_url: str
    universe: str
    created_at: datetime
    username: str

class SimilarUser(BaseModel):
    user_id: str
    username: str
    avatar_url: Optional[str]
    shared_styles: int

class GenerateAlterEgoResponse(BaseModel):
    id: str
    image_url: str
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_schemas.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/models/schemas.py tests/test_schemas.py
git commit -m "feat: add pydantic schemas"
```

---

## Task 4: Domain Layer (Abstract Interfaces + Use Cases)

**Files:**
- Create: `backend/app/domain/__init__.py`
- Create: `backend/app/domain/repositories/__init__.py`
- Create: `backend/app/domain/repositories/alter_ego_repository.py`
- Create: `backend/app/domain/repositories/user_repository.py`
- Create: `backend/app/domain/repositories/feed_repository.py`
- Create: `backend/app/domain/repositories/like_repository.py`
- Create: `backend/app/domain/usecases/__init__.py`
- Create: `backend/app/domain/usecases/generate_alter_ego_usecase.py`
- Create: `backend/app/domain/usecases/get_feed_usecase.py`
- Create: `backend/app/domain/usecases/get_similar_users_usecase.py`
- Create: `backend/tests/test_usecases.py`

- [ ] **Step 1: Write failing tests first (TDD)**

```python
# backend/tests/test_usecases.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.domain.usecases.get_feed_usecase import GetFeedUseCase
from app.domain.usecases.get_similar_users_usecase import GetSimilarUsersUseCase

@pytest.mark.asyncio
async def test_get_feed_calls_repository():
    mock_repo = MagicMock()
    mock_repo.get_recent = AsyncMock(return_value=[{"id": "1", "image_url": "https://x.com/img.png"}])
    usecase = GetFeedUseCase(feed_repository=mock_repo)
    result = await usecase.execute(limit=10, offset=0)
    mock_repo.get_recent.assert_called_once_with(limit=10, offset=0)
    assert len(result) == 1

@pytest.mark.asyncio
async def test_get_similar_users_calls_repository():
    mock_repo = MagicMock()
    mock_repo.find_similar_ids = AsyncMock(return_value=[])
    usecase = GetSimilarUsersUseCase(user_repository=mock_repo)
    result = await usecase.execute(user_id="user-1", limit=10)
    mock_repo.find_similar_ids.assert_called_once_with(user_id="user-1", limit=10)
    assert result == []
```

- [ ] **Step 2: Run to verify they fail**

```bash
cd backend && python -m pytest tests/test_usecases.py -v
```
Expected: ModuleNotFoundError

- [ ] **Step 3: Create domain directory structure**

```bash
mkdir -p backend/app/domain/repositories backend/app/domain/usecases
touch backend/app/domain/__init__.py
touch backend/app/domain/repositories/__init__.py
touch backend/app/domain/usecases/__init__.py
```

- [ ] **Step 4: Write abstract repository interfaces**

```python
# backend/app/domain/repositories/alter_ego_repository.py
from abc import ABC, abstractmethod

class AlterEgoRepository(ABC):
    @abstractmethod
    async def save(self, user_id: str, image_url: str, selfie_url: str, universe: str, traits: dict) -> dict:
        ...

    @abstractmethod
    async def find_by_ids(self, ids: list[str]) -> list[dict]:
        ...
```

```python
# backend/app/domain/repositories/user_repository.py
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    async def find_by_ids(self, ids: list[str]) -> list[dict]:
        ...

    @abstractmethod
    async def find_similar_ids(self, user_id: str, limit: int = 10) -> list[dict]:
        ...
```

```python
# backend/app/domain/repositories/feed_repository.py
from abc import ABC, abstractmethod

class FeedRepository(ABC):
    @abstractmethod
    async def get_recent(self, limit: int = 20, offset: int = 0) -> list[dict]:
        ...
```

```python
# backend/app/domain/repositories/like_repository.py
from abc import ABC, abstractmethod

class LikeRepository(ABC):
    @abstractmethod
    async def save(self, user_id: str, alter_ego_id: str) -> None:
        ...
```

- [ ] **Step 5: Write use cases**

```python
# backend/app/domain/usecases/generate_alter_ego_usecase.py
from app.domain.repositories.alter_ego_repository import AlterEgoRepository
from app.services.vision_service import VisionService
from app.services.prompt_service import PromptService
from app.services.generation_service import GenerationService

class GenerateAlterEgoUseCase:
    def __init__(
        self,
        alter_ego_repository: AlterEgoRepository,
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
        )
        return {"id": saved["id"], "image_url": image_url, "style_tags": style_tags}
```

```python
# backend/app/domain/usecases/get_feed_usecase.py
from app.domain.repositories.feed_repository import FeedRepository

class GetFeedUseCase:
    def __init__(self, feed_repository: FeedRepository):
        self._repo = feed_repository

    async def execute(self, limit: int = 20, offset: int = 0) -> list[dict]:
        return await self._repo.get_recent(limit=limit, offset=offset)
```

```python
# backend/app/domain/usecases/get_similar_users_usecase.py
from app.domain.repositories.user_repository import UserRepository

class GetSimilarUsersUseCase:
    def __init__(self, user_repository: UserRepository):
        self._repo = user_repository

    async def execute(self, user_id: str, limit: int = 10) -> list[dict]:
        return await self._repo.find_similar_ids(user_id=user_id, limit=limit)
```

- [ ] **Step 6: Run tests**

```bash
cd backend && python -m pytest tests/test_usecases.py -v
```
Expected: PASS

- [ ] **Step 7: Run full test suite to ensure nothing broke**

```bash
cd backend && python -m pytest -v
```
Expected: all PASS

**DO NOT commit anything.**

---

## Task 5: Supabase Postgres Setup

**Files:**
- Create: `backend/supabase_migrations.sql`
- Create: `backend/app/repositories/alter_ego_pg_repository.py`
- Create: `backend/app/repositories/user_pg_repository.py`
- Create: `backend/app/repositories/like_repository.py` (Postgres side)

- [ ] **Step 1: Write the SQL migrations**

Run these in Supabase SQL editor:

```sql
-- profiles (extends Supabase Auth users)
CREATE TABLE profiles (
  id         UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  username   TEXT NOT NULL UNIQUE,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- alter_egos
CREATE TABLE alter_egos (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  image_url   TEXT NOT NULL,
  selfie_url  TEXT NOT NULL,
  universe    TEXT NOT NULL,
  traits      JSONB DEFAULT '{}',
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- likes
CREATE TABLE likes (
  user_id      UUID REFERENCES profiles(id) ON DELETE CASCADE,
  alter_ego_id UUID REFERENCES alter_egos(id) ON DELETE CASCADE,
  created_at   TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (user_id, alter_ego_id)
);

-- Storage bucket for images
INSERT INTO storage.buckets (id, name, public) VALUES ('alter-egos', 'alter-egos', true);
```

Save this file as `backend/supabase_migrations.sql`.

- [ ] **Step 2: Write failing test for alter_ego_pg_repository**

```python
# tests/test_alter_ego_pg_repository.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.repositories.alter_ego_pg_repository import AlterEgoPgRepository

@pytest.fixture
def mock_client():
    client = MagicMock()
    client.table.return_value.insert.return_value.execute = AsyncMock(
        return_value=MagicMock(data=[{
            "id": "uuid-123",
            "user_id": "user-1",
            "image_url": "https://example.com/img.png",
            "universe": "anime",
            "traits": {"expression": "smiling"},
            "created_at": "2026-06-12T00:00:00",
        }])
    )
    return client

@pytest.mark.asyncio
async def test_save_returns_alter_ego(mock_client):
    repo = AlterEgoPgRepository(client=mock_client)
    result = await repo.save(
        user_id="user-1",
        image_url="https://example.com/img.png",
        selfie_url="https://example.com/selfie.png",
        universe="anime",
        traits={"expression": "smiling"},
    )
    assert result["id"] == "uuid-123"
```

- [ ] **Step 3: Run to verify it fails**

```bash
python -m pytest tests/test_alter_ego_pg_repository.py -v
```

- [ ] **Step 4: Write app/repositories/alter_ego_pg_repository.py**

```python
from typing import Any

class AlterEgoPgRepository:
    def __init__(self, client):
        self._client = client

    async def save(self, user_id: str, image_url: str, selfie_url: str, universe: str, traits: dict) -> dict:
        result = await self._client.table("alter_egos").insert({
            "user_id": user_id,
            "image_url": image_url,
            "selfie_url": selfie_url,
            "universe": universe,
            "traits": traits,
        }).execute()
        return result.data[0]

    async def find_by_ids(self, ids: list[str]) -> list[dict]:
        result = await self._client.table("alter_egos").select(
            "id, image_url, universe, created_at, profiles(username)"
        ).in_("id", ids).execute()
        return result.data
```

- [ ] **Step 5: Write app/repositories/user_pg_repository.py**

```python
class UserPgRepository:
    def __init__(self, client):
        self._client = client

    async def find_by_ids(self, ids: list[str]) -> list[dict]:
        result = await self._client.table("profiles").select(
            "id, username, avatar_url"
        ).in_("id", ids).execute()
        return result.data
```

- [ ] **Step 6: Write app/repositories/like_repository.py**

```python
class LikeRepository:
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
```

- [ ] **Step 7: Run tests**

```bash
python -m pytest tests/test_alter_ego_pg_repository.py -v
```
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add backend/app/repositories/ backend/supabase_migrations.sql tests/
git commit -m "feat: add postgres repositories and migrations"
```

---

## Task 5: Neo4j Graph Repositories

**Files:**
- Create: `backend/app/repositories/alter_ego_graph_repository.py`
- Create: `backend/app/repositories/user_graph_repository.py`
- Create: `backend/app/repositories/feed_repository.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_alter_ego_graph_repository.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.repositories.alter_ego_graph_repository import AlterEgoGraphRepository

@pytest.fixture
def mock_driver():
    driver = MagicMock()
    session = AsyncMock()
    driver.session.return_value.__aenter__ = AsyncMock(return_value=session)
    driver.session.return_value.__aexit__ = AsyncMock(return_value=False)
    return driver, session

@pytest.mark.asyncio
async def test_save_creates_node_and_edges(mock_driver):
    driver, session = mock_driver
    repo = AlterEgoGraphRepository(driver=driver)
    await repo.save(
        user_id="user-1",
        alter_ego_id="ae-1",
        styles=["anime", "smiling", "black_hair"],
    )
    assert session.run.call_count == 2  # node creation + style edges
```

- [ ] **Step 2: Run to verify it fails**

```bash
python -m pytest tests/test_alter_ego_graph_repository.py -v
```

- [ ] **Step 3: Write app/repositories/alter_ego_graph_repository.py**

```python
class AlterEgoGraphRepository:
    def __init__(self, driver):
        self._driver = driver

    async def save(self, user_id: str, alter_ego_id: str, styles: list[str]) -> None:
        async with self._driver.session() as session:
            await session.run(
                "MERGE (u:User {id: $uid}) "
                "MERGE (a:AlterEgo {id: $aid}) "
                "MERGE (u)-[:CREATED]->(a)",
                uid=user_id, aid=alter_ego_id,
            )
            for style in styles:
                await session.run(
                    "MERGE (s:Style {name: $style}) "
                    "MERGE (a:AlterEgo {id: $aid}) "
                    "MERGE (a)-[:HAS_STYLE]->(s)",
                    style=style, aid=alter_ego_id,
                )
```

- [ ] **Step 4: Write app/repositories/user_graph_repository.py**

```python
class UserGraphRepository:
    def __init__(self, driver):
        self._driver = driver

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
```

- [ ] **Step 5: Write app/repositories/feed_repository.py**

```python
from app.repositories.alter_ego_graph_repository import AlterEgoGraphRepository
from app.repositories.alter_ego_pg_repository import AlterEgoPgRepository

class FeedRepository:
    def __init__(self, graph_repo: AlterEgoGraphRepository, pg_repo: AlterEgoPgRepository, driver):
        self._driver = driver
        self._pg_repo = pg_repo

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
```

- [ ] **Step 6: Run tests**

```bash
python -m pytest tests/test_alter_ego_graph_repository.py -v
```
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add backend/app/repositories/
git commit -m "feat: add neo4j graph repositories and feed repository"
```

---

## Task 6: Vision Service

**Files:**
- Create: `backend/app/services/vision_service.py`
- Create: `backend/tests/test_vision_service.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_vision_service.py
import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.services.vision_service import VisionService
from app.core.errors import VisionError

MOCK_VISION_RESPONSE = {
    "responses": [{
        "faceAnnotations": [{
            "joyLikelihood": "VERY_LIKELY",
            "sorrowLikelihood": "UNLIKELY",
        }],
        "imagePropertiesAnnotation": {
            "dominantColors": {
                "colors": [{"color": {"red": 0, "green": 0, "blue": 0}, "score": 0.9}]
            }
        },
        "labelAnnotations": [
            {"description": "face", "score": 0.99},
            {"description": "hair", "score": 0.85},
        ]
    }]
}

@pytest.mark.asyncio
async def test_extract_traits_returns_dict():
    service = VisionService(api_key="fake-key")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(200, json=MOCK_VISION_RESPONSE)
        traits = await service.extract_traits("https://example.com/selfie.png")
    assert isinstance(traits, dict)
    assert "expression" in traits

@pytest.mark.asyncio
async def test_extract_traits_raises_vision_error_on_failure():
    service = VisionService(api_key="fake-key")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(400, json={"error": "bad request"})
        with pytest.raises(VisionError):
            await service.extract_traits("https://example.com/selfie.png")
```

- [ ] **Step 2: Run to verify it fails**

```bash
python -m pytest tests/test_vision_service.py -v
```

- [ ] **Step 3: Write app/services/vision_service.py**

```python
import httpx
from app.core.errors import VisionError

VISION_URL = "https://vision.googleapis.com/v1/images:annotate"

class VisionService:
    def __init__(self, api_key: str):
        self._api_key = api_key

    async def extract_traits(self, image_url: str) -> dict:
        payload = {
            "requests": [{
                "image": {"source": {"imageUri": image_url}},
                "features": [
                    {"type": "FACE_DETECTION"},
                    {"type": "IMAGE_PROPERTIES"},
                    {"type": "LABEL_DETECTION", "maxResults": 5},
                ],
            }]
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{VISION_URL}?key={self._api_key}",
                json=payload,
            )

        if response.status_code != 200:
            raise VisionError(f"Vision API error: {response.text}")

        return self._parse_traits(response.json())

    def _parse_traits(self, data: dict) -> dict:
        response = data.get("responses", [{}])[0]
        traits = {}

        faces = response.get("faceAnnotations", [])
        if faces:
            face = faces[0]
            if face.get("joyLikelihood") in ("LIKELY", "VERY_LIKELY"):
                traits["expression"] = "smiling"
            elif face.get("sorrowLikelihood") in ("LIKELY", "VERY_LIKELY"):
                traits["expression"] = "sad"
            else:
                traits["expression"] = "neutral"

        colors = response.get("imagePropertiesAnnotation", {}).get("dominantColors", {}).get("colors", [])
        if colors:
            top = colors[0]["color"]
            r, g, b = top.get("red", 0), top.get("green", 0), top.get("blue", 0)
            if r > 150 and g < 100:
                traits["hair_color"] = "red"
            elif r < 80 and g < 80 and b < 80:
                traits["hair_color"] = "black"
            elif r > 200 and g > 200 and b > 200:
                traits["hair_color"] = "blonde"
            else:
                traits["hair_color"] = "brown"

        labels = [l["description"].lower() for l in response.get("labelAnnotations", [])]
        traits["labels"] = labels

        return traits
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_vision_service.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/vision_service.py backend/tests/test_vision_service.py
git commit -m "feat: add vision service with trait extraction"
```

---

## Task 7: Prompt and Generation Services

**Files:**
- Create: `backend/app/services/prompt_service.py`
- Create: `backend/app/services/generation_service.py`
- Create: `backend/tests/test_prompt_service.py`
- Create: `backend/tests/test_generation_service.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_prompt_service.py
from app.services.prompt_service import PromptService

def test_builds_anime_prompt():
    service = PromptService()
    prompt = service.build_prompt(
        traits={"expression": "smiling", "hair_color": "black"},
        universe="anime",
    )
    assert "anime" in prompt.lower()
    assert "smiling" in prompt.lower() or "smile" in prompt.lower()

def test_prompt_includes_quality_suffix():
    service = PromptService()
    prompt = service.build_prompt(traits={}, universe="medieval")
    assert "high quality" in prompt.lower() or "detailed" in prompt.lower()
```

```python
# tests/test_generation_service.py
import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.services.generation_service import GenerationService
from app.core.errors import GenerationError

@pytest.mark.asyncio
async def test_generate_returns_image_url():
    service = GenerationService(api_token="fake-token")
    mock_output = ["https://replicate.delivery/output/img.png"]
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(201, json={"output": mock_output, "status": "succeeded"})
        with patch.object(service, "_poll_until_done", new_callable=AsyncMock) as mock_poll:
            mock_poll.return_value = "https://replicate.delivery/output/img.png"
            url = await service.generate("a cool prompt")
    assert url.startswith("https://")

@pytest.mark.asyncio
async def test_generate_raises_on_api_failure():
    service = GenerationService(api_token="fake-token")
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = httpx.Response(422, json={"detail": "invalid"})
        with pytest.raises(GenerationError):
            await service.generate("prompt")
```

- [ ] **Step 2: Run to verify they fail**

```bash
python -m pytest tests/test_prompt_service.py tests/test_generation_service.py -v
```

- [ ] **Step 3: Write app/services/prompt_service.py**

```python
UNIVERSE_DESCRIPTORS = {
    "anime": "anime art style, vibrant colors, large expressive eyes, Studio Ghibli quality",
    "medieval": "medieval fantasy portrait, oil painting, armor, castle background",
    "sci-fi": "futuristic cyberpunk portrait, neon lights, chrome, holographic elements",
    "político br": "brazilian political caricature, editorial cartoon style, exaggerated features",
}

QUALITY_SUFFIX = ", highly detailed, 8k, professional illustration"

class PromptService:
    def build_prompt(self, traits: dict, universe: str) -> str:
        base = UNIVERSE_DESCRIPTORS.get(universe.lower(), f"{universe} art style")
        parts = [f"portrait of a person in {base}"]

        if traits.get("expression"):
            parts.append(f"with a {traits['expression']} expression")

        if traits.get("hair_color"):
            parts.append(f"{traits['hair_color']} hair")

        return ", ".join(parts) + QUALITY_SUFFIX

    def extract_style_tags(self, traits: dict, universe: str) -> list[str]:
        tags = [universe.lower()]
        if traits.get("expression"):
            tags.append(traits["expression"])
        if traits.get("hair_color"):
            tags.append(traits["hair_color"] + "_hair")
        return tags
```

- [ ] **Step 4: Write app/services/generation_service.py**

```python
import asyncio
import httpx
from app.core.errors import GenerationError

REPLICATE_API_URL = "https://api.replicate.com/v1/predictions"
MODEL_VERSION = "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"  # SDXL

class GenerationService:
    def __init__(self, api_token: str):
        self._token = api_token

    async def generate(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Token {self._token}",
            "Content-Type": "application/json",
        }
        payload = {
            "version": MODEL_VERSION,
            "input": {"prompt": prompt, "width": 768, "height": 768},
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(REPLICATE_API_URL, json=payload, headers=headers)

        if response.status_code not in (200, 201):
            raise GenerationError(f"Replicate API error: {response.text}")

        prediction = response.json()
        return await self._poll_until_done(prediction["id"], headers)

    async def _poll_until_done(self, prediction_id: str, headers: dict) -> str:
        url = f"{REPLICATE_API_URL}/{prediction_id}"
        async with httpx.AsyncClient() as client:
            for _ in range(30):
                response = await client.get(url, headers=headers)
                data = response.json()
                if data["status"] == "succeeded":
                    return data["output"][0]
                if data["status"] == "failed":
                    raise GenerationError("Image generation failed")
                await asyncio.sleep(2)
        raise GenerationError("Generation timed out")
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests/test_prompt_service.py tests/test_generation_service.py -v
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/ backend/tests/
git commit -m "feat: add prompt and generation services"
```

---

## Task 8: Alter Ego Handler

**Files:**
- Create: `backend/app/handlers/alter_ego_handler.py`
- Create: `backend/tests/test_alter_ego_handler.py`
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: Write conftest.py**

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

@pytest.fixture
def mock_vision_service(mocker):
    return mocker.patch(
        "app.handlers.alter_ego_handler.VisionService.extract_traits",
        new_callable=AsyncMock,
        return_value={"expression": "smiling", "hair_color": "black"},
    )

@pytest.fixture
def mock_generation_service(mocker):
    return mocker.patch(
        "app.handlers.alter_ego_handler.GenerationService.generate",
        new_callable=AsyncMock,
        return_value="https://replicate.delivery/output/result.png",
    )
```

- [ ] **Step 2: Write failing test**

```python
# tests/test_alter_ego_handler.py
import pytest

@pytest.mark.asyncio
async def test_generate_returns_image_url(client, mock_vision_service, mock_generation_service, mocker):
    mocker.patch(
        "app.handlers.alter_ego_handler.AlterEgoPgRepository.save",
        new_callable=AsyncMock,
        return_value={"id": "ae-uuid-1", "image_url": "https://replicate.delivery/output/result.png"},
    )
    mocker.patch(
        "app.handlers.alter_ego_handler.AlterEgoGraphRepository.save",
        new_callable=AsyncMock,
    )

    response = await client.post("/alter-ego/generate", json={
        "selfie_url": "https://example.com/selfie.png",
        "universe": "anime",
        "user_id": "user-1",
    })

    assert response.status_code == 200
    assert "image_url" in response.json()

@pytest.mark.asyncio
async def test_generate_returns_422_on_missing_fields(client):
    response = await client.post("/alter-ego/generate", json={})
    assert response.status_code == 422
```

- [ ] **Step 3: Run to verify it fails**

```bash
python -m pytest tests/test_alter_ego_handler.py -v
```

- [ ] **Step 4: Write app/handlers/alter_ego_handler.py**

```python
from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import GenerateAlterEgoRequest, GenerateAlterEgoResponse, LikeRequest
from app.services.vision_service import VisionService
from app.services.prompt_service import PromptService
from app.services.generation_service import GenerationService
from app.repositories.alter_ego_pg_repository import AlterEgoPgRepository
from app.repositories.alter_ego_graph_repository import AlterEgoGraphRepository
from app.repositories.like_repository import LikeRepository
from app.core.config import settings
from app.core.errors import VisionError, GenerationError

router = APIRouter()

def _vision_service() -> VisionService:
    return VisionService(api_key=settings.google_vision_api_key)

def _generation_service() -> GenerationService:
    return GenerationService(api_token=settings.replicate_api_token)

@router.post("/generate", response_model=GenerateAlterEgoResponse)
async def generate_alter_ego(
    body: GenerateAlterEgoRequest,
    vision: VisionService = Depends(_vision_service),
    generation: GenerationService = Depends(_generation_service),
):
    try:
        traits = await vision.extract_traits(body.selfie_url)
    except VisionError as e:
        raise HTTPException(status_code=502, detail=str(e))

    prompt_service = PromptService()
    prompt = prompt_service.build_prompt(traits, body.universe)
    styles = prompt_service.extract_style_tags(traits, body.universe)

    try:
        image_url = await generation.generate(prompt)
    except GenerationError as e:
        raise HTTPException(status_code=502, detail=str(e))

    from supabase import create_client
    pg_client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    pg_repo = AlterEgoPgRepository(client=pg_client)
    saved = await pg_repo.save(
        user_id=body.user_id,
        image_url=image_url,
        selfie_url=body.selfie_url,
        universe=body.universe,
        traits=traits,
    )

    from neo4j import AsyncGraphDatabase
    driver = AsyncGraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))
    graph_repo = AlterEgoGraphRepository(driver=driver)
    await graph_repo.save(user_id=body.user_id, alter_ego_id=saved["id"], styles=styles)
    await driver.close()

    return GenerateAlterEgoResponse(id=saved["id"], image_url=image_url)

@router.post("/{alter_ego_id}/like")
async def like_alter_ego(alter_ego_id: str, body: LikeRequest):
    from supabase import create_client
    from neo4j import AsyncGraphDatabase
    pg_client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    driver = AsyncGraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))
    repo = LikeRepository(pg_client=pg_client, graph_driver=driver)
    await repo.save(user_id=body.user_id, alter_ego_id=alter_ego_id)
    await driver.close()
    return {"ok": True}
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests/test_alter_ego_handler.py -v
```
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/app/handlers/alter_ego_handler.py backend/tests/
git commit -m "feat: add alter ego handler (generate + like)"
```

---

## Task 9: Feed and Profile Handlers

**Files:**
- Create: `backend/app/handlers/feed_handler.py`
- Create: `backend/app/handlers/profile_handler.py`
- Create: `backend/tests/test_feed_handler.py`
- Create: `backend/tests/test_profile_handler.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_feed_handler.py
import pytest

@pytest.mark.asyncio
async def test_feed_returns_list(client, mocker):
    mocker.patch(
        "app.handlers.feed_handler.FeedRepository.get_recent",
        new_callable=AsyncMock,
        return_value=[],
    )
    response = await client.get("/feed")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

```python
# tests/test_profile_handler.py
import pytest

@pytest.mark.asyncio
async def test_similar_users_returns_list(client, mocker):
    mocker.patch(
        "app.handlers.profile_handler.UserGraphRepository.find_similar_ids",
        new_callable=AsyncMock,
        return_value=[],
    )
    response = await client.get("/profile/user-1/similar")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

- [ ] **Step 2: Run to verify they fail**

```bash
python -m pytest tests/test_feed_handler.py tests/test_profile_handler.py -v
```

- [ ] **Step 3: Write app/handlers/feed_handler.py**

```python
from fastapi import APIRouter
from app.repositories.feed_repository import FeedRepository
from app.repositories.alter_ego_graph_repository import AlterEgoGraphRepository
from app.repositories.alter_ego_pg_repository import AlterEgoPgRepository
from app.core.config import settings

router = APIRouter()

@router.get("")
async def get_feed(limit: int = 20, offset: int = 0):
    from supabase import create_client
    from neo4j import AsyncGraphDatabase
    pg_client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    driver = AsyncGraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))
    pg_repo = AlterEgoPgRepository(client=pg_client)
    graph_repo = AlterEgoGraphRepository(driver=driver)
    feed_repo = FeedRepository(graph_repo=graph_repo, pg_repo=pg_repo, driver=driver)
    result = await feed_repo.get_recent(limit=limit, offset=offset)
    await driver.close()
    return result
```

- [ ] **Step 4: Write app/handlers/profile_handler.py**

```python
from fastapi import APIRouter
from app.repositories.user_graph_repository import UserGraphRepository
from app.repositories.user_pg_repository import UserPgRepository
from app.core.config import settings

router = APIRouter()

@router.get("/{user_id}/similar")
async def get_similar_users(user_id: str, limit: int = 10):
    from neo4j import AsyncGraphDatabase
    from supabase import create_client
    driver = AsyncGraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))
    graph_repo = UserGraphRepository(driver=driver)
    similar = await graph_repo.find_similar_ids(user_id=user_id, limit=limit)
    await driver.close()

    if not similar:
        return []

    pg_client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    pg_repo = UserPgRepository(client=pg_client)
    ids = [s["user_id"] for s in similar]
    users = await pg_repo.find_by_ids(ids)

    shared_map = {s["user_id"]: s["shared_styles"] for s in similar}
    return [
        {**u, "shared_styles": shared_map.get(u["id"], 0)}
        for u in users
    ]
```

- [ ] **Step 5: Run tests**

```bash
python -m pytest tests/test_feed_handler.py tests/test_profile_handler.py -v
```
Expected: PASS

- [ ] **Step 6: Run full test suite**

```bash
python -m pytest -v
```
Expected: all tests PASS

- [ ] **Step 7: Commit**

```bash
git add backend/app/handlers/ backend/tests/
git commit -m "feat: add feed and profile handlers"
```

---

## Task 10: Auth Middleware

**Files:**
- Create: `backend/app/middleware/auth.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_auth_middleware.py
import pytest
from app.middleware.auth import verify_supabase_token
from app.core.errors import NotFoundError

def test_invalid_token_raises():
    with pytest.raises(Exception):
        verify_supabase_token("invalid.token.here")
```

- [ ] **Step 2: Run to verify it fails**

```bash
python -m pytest tests/test_auth_middleware.py -v
```

- [ ] **Step 3: Write app/middleware/auth.py**

```python
from fastapi import Header, HTTPException
from jose import jwt, JWTError
from app.core.config import settings

def verify_supabase_token(authorization: str = Header(...)) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

To protect a route, add `Depends(verify_supabase_token)` to the handler parameter list.

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_auth_middleware.py -v
```
Expected: PASS

- [ ] **Step 5: Run full suite and start server**

```bash
python -m pytest -v
cd backend && uvicorn app.main:app --reload
```
Expected: server running at http://localhost:8000, all tests PASS

- [ ] **Step 6: Final commit**

```bash
git add backend/app/middleware/ backend/tests/test_auth_middleware.py
git commit -m "feat: add Supabase JWT auth middleware"
```
