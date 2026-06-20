from abc import ABC, abstractmethod


class AlterEgoRepository(ABC):
    @abstractmethod
    async def save(self, user_id: str, image_url: str, selfie_url: str, universe: str, traits: dict) -> dict:
        ...

    @abstractmethod
    async def find_by_ids(self, ids: list[str]) -> list[dict]:
        ...
