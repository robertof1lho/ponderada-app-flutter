import pytest
from unittest.mock import AsyncMock
from app.main import app
from app.handlers.alter_ego_handler import _make_generate_usecase
from app.middleware.auth import verify_jwt_token
from app.core.errors import VisionError, GenerationError

MOCK_CLAIMS = {"sub": "user-1"}


@pytest.mark.asyncio
async def test_generate_returns_200(client, mocker):
    mock_usecase = mocker.MagicMock()
    mock_usecase.execute = AsyncMock(return_value={
        "id": "ae-1",
        "image_url": "https://example.com/img.png",
        "style_tags": ["anime"],
    })
    app.dependency_overrides[_make_generate_usecase] = lambda: mock_usecase
    app.dependency_overrides[verify_jwt_token] = lambda: MOCK_CLAIMS
    response = await client.post("/alter-ego/generate", json={
        "selfie_url": "https://example.com/selfie.png",
        "universe": "anime",
    })
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert "image_url" in response.json()


@pytest.mark.asyncio
async def test_generate_returns_422_on_missing_fields(client, mocker):
    mock_usecase = mocker.MagicMock()
    app.dependency_overrides[_make_generate_usecase] = lambda: mock_usecase
    app.dependency_overrides[verify_jwt_token] = lambda: MOCK_CLAIMS
    response = await client.post("/alter-ego/generate", json={})
    app.dependency_overrides.clear()
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_returns_502_on_vision_error(client, mocker):
    mock_usecase = mocker.MagicMock()
    mock_usecase.execute = AsyncMock(side_effect=VisionError("Vision failed"))
    app.dependency_overrides[_make_generate_usecase] = lambda: mock_usecase
    app.dependency_overrides[verify_jwt_token] = lambda: MOCK_CLAIMS
    response = await client.post("/alter-ego/generate", json={
        "selfie_url": "https://example.com/selfie.png",
        "universe": "anime",
    })
    app.dependency_overrides.clear()
    assert response.status_code == 502


@pytest.mark.asyncio
async def test_generate_returns_502_on_generation_error(client, mocker):
    mock_usecase = mocker.MagicMock()
    mock_usecase.execute = AsyncMock(side_effect=GenerationError("HF failed"))
    app.dependency_overrides[_make_generate_usecase] = lambda: mock_usecase
    app.dependency_overrides[verify_jwt_token] = lambda: MOCK_CLAIMS
    response = await client.post("/alter-ego/generate", json={
        "selfie_url": "https://example.com/selfie.png",
        "universe": "anime",
    })
    app.dependency_overrides.clear()
    assert response.status_code == 502


