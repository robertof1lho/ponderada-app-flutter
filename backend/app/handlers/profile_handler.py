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
