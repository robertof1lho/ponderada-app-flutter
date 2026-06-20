from fastapi import APIRouter, Depends
from app.domain.usecases.get_feed_usecase import GetFeedUseCase
from app.core.config import settings

router = APIRouter()


def _make_feed_usecase() -> GetFeedUseCase:
    from supabase import create_client
    from neo4j import AsyncGraphDatabase
    from app.repositories.alter_ego_pg_repository import AlterEgoPgRepository
    from app.repositories.feed_repository import FeedRepository

    pg_client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
    )
    pg_repo = AlterEgoPgRepository(client=pg_client)
    feed_repo = FeedRepository(pg_repo=pg_repo, driver=driver)
    return GetFeedUseCase(feed_repository=feed_repo)


@router.get("")
async def get_feed(
    limit: int = 20,
    offset: int = 0,
    usecase: GetFeedUseCase = Depends(_make_feed_usecase),
):
    return await usecase.execute(limit=limit, offset=offset)
