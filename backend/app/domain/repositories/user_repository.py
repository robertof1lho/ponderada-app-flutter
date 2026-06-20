from abc import ABC, abstractmethod


class UserRepository(ABC):
    @abstractmethod
    async def find_by_ids(self, ids: list[str]) -> list[dict]:
        ...

    @abstractmethod
    async def find_similar_ids(self, user_id: str, limit: int = 10) -> list[dict]:
        ...
