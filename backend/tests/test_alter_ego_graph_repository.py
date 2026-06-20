import pytest
from unittest.mock import AsyncMock, MagicMock
from app.repositories.alter_ego_graph_repository import AlterEgoGraphRepository

@pytest.fixture
def mock_driver():
    driver = MagicMock()
    session = AsyncMock()
    driver.session.return_value.__aenter__ = AsyncMock(return_value=session)
    driver.session.return_value.__aexit__ = AsyncMock(return_value=False)
    return driver, session

@pytest.mark.asyncio
async def test_save_graph_creates_nodes_and_edges(mock_driver):
    driver, session = mock_driver
    repo = AlterEgoGraphRepository(driver=driver)
    await repo.save_graph(
        user_id="user-1",
        alter_ego_id="ae-1",
        styles=["anime", "smiling", "black_hair"],
    )
    assert session.run.call_count == 2  # 1 for nodes + 1 for UNWIND styles

@pytest.mark.asyncio
async def test_save_graph_with_no_styles(mock_driver):
    driver, session = mock_driver
    repo = AlterEgoGraphRepository(driver=driver)
    await repo.save_graph(user_id="user-1", alter_ego_id="ae-1", styles=[])
    assert session.run.call_count == 1  # only node creation, no style batch
