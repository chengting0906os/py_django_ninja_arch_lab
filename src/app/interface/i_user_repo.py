"""User repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entity.user_entity import User


class IUserRepo(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        pass
