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


@router.delete("/{alter_ego_id}", status_code=204)
async def delete_alter_ego(
    alter_ego_id: str,
    claims: dict = Depends(verify_jwt_token),
    usecase: GenerateAlterEgoUseCase = Depends(_make_generate_usecase),
):
    from app.core.db import get_pool
    from app.repositories.alter_ego_mysql_repository import AlterEgoMysqlRepository
    pool = await get_pool()
    repo = AlterEgoMysqlRepository(pool=pool)
    deleted = await repo.delete(alter_ego_id=alter_ego_id, user_id=claims["sub"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Alter ego not found or not yours")


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
