from fastapi import APIRouter, Depends, HTTPException
from app.domain.usecases.get_similar_users_usecase import GetSimilarUsersUseCase
from app.middleware.auth import verify_supabase_token
from app.core.config import settings

router = APIRouter()

def _make_similar_users_usecase() -> GetSimilarUsersUseCase:
    from supabase import create_client
    from neo4j import AsyncGraphDatabase
    from app.repositories.user_graph_repository import UserGraphRepository
    pg_client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
    )
    graph_repo = UserGraphRepository(driver=driver)
    return GetSimilarUsersUseCase(user_repository=graph_repo)

@router.get("/{user_id}/similar")
async def get_similar_users(
    user_id: str,
    limit: int = 10,
    claims: dict = Depends(verify_supabase_token),
    usecase: GetSimilarUsersUseCase = Depends(_make_similar_users_usecase),
):
    if claims["sub"] != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await usecase.execute(user_id=user_id, limit=limit)
