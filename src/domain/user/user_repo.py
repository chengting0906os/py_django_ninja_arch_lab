"""User repository interface."""

from abc import ABC, abstractmethod
from typing import Optional

from .user_model import User


class UserRepo(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        pass
