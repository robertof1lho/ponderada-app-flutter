from abc import ABC, abstractmethod


class FeedRepository(ABC):
    @abstractmethod
    async def get_recent(self, limit: int = 20, offset: int = 0) -> list[dict]:
        ...
