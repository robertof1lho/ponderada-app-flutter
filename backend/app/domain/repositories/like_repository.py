from abc import ABC, abstractmethod


class LikeRepository(ABC):
    @abstractmethod
    async def save(self, user_id: str, alter_ego_id: str) -> None:
        ...
