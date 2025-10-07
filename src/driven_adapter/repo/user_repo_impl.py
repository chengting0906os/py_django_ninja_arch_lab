"""User repository implementation."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.platform.logging.loguru_io import Logger
from src.driven_adapter.model.user_model import User as UserModel
from src.domain.entity.user_entity import User
from src.domain.enum.user_role_enum import UserRole
from src.app.interface.i_user_repo import IUserRepo


class UserRepoImpl(IUserRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_entity(db_user: UserModel) -> User:
        return User(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            role=UserRole(db_user.role),
        )

    @Logger.io
    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        db_user = result.scalar_one_or_none()
        if not db_user:
            return None
        return self._to_entity(db_user)
