from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import GenerateAlterEgoRequest, GenerateAlterEgoResponse, LikeRequest
from app.domain.usecases.generate_alter_ego_usecase import GenerateAlterEgoUseCase
from app.domain.repositories.like_repository import LikeRepository
from app.core.config import settings
from app.core.errors import VisionError, GenerationError
from app.middleware.auth import verify_supabase_token

router = APIRouter()


def _make_generate_usecase() -> GenerateAlterEgoUseCase:
    from supabase import create_client
    from neo4j import AsyncGraphDatabase
    from app.services.vision_service import VisionService
    from app.services.prompt_service import PromptService
    from app.services.generation_service import GenerationService
    from app.repositories.alter_ego_pg_repository import AlterEgoPgRepository
    from app.repositories.alter_ego_graph_repository import AlterEgoGraphRepository

    pg_client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
    )
    return GenerateAlterEgoUseCase(
        alter_ego_pg_repository=AlterEgoPgRepository(client=pg_client),
        alter_ego_graph_repository=AlterEgoGraphRepository(driver=driver),
        vision_service=VisionService(api_key=settings.google_vision_api_key),
        prompt_service=PromptService(),
        generation_service=GenerationService(api_token=settings.replicate_api_token),
    )


def _make_like_repository() -> LikeRepository:
    from supabase import create_client
    from neo4j import AsyncGraphDatabase
    from app.repositories.like_repository import LikeRepository as LikeRepositoryImpl

    pg_client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
    )
    return LikeRepositoryImpl(pg_client=pg_client, graph_driver=driver)


@router.post("/generate", response_model=GenerateAlterEgoResponse)
async def generate_alter_ego(
    body: GenerateAlterEgoRequest,
    claims: dict = Depends(verify_supabase_token),
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
    claims: dict = Depends(verify_supabase_token),
    repo: LikeRepository = Depends(_make_like_repository),
):
    await repo.save(user_id=claims["sub"], alter_ego_id=alter_ego_id)
    return {"ok": True}
