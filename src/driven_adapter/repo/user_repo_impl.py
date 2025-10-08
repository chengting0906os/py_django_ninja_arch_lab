"""User repository implementation backed by Django ORM."""

from __future__ import annotations

from typing import Optional

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

from src.app.interface.i_user_repo import IUserRepo
from src.domain.entity.user_entity import User
from src.domain.enum.user_role_enum import UserRole
from src.platform.logging.loguru_io import Logger


UserModel = get_user_model()


class UserRepoImpl(IUserRepo):
    @staticmethod
    def _to_entity(db_user: UserModel) -> User:  # type: ignore[type-arg]
        return User(
            id=db_user.id,
            email=db_user.email,
            name=db_user.email,  # Use email as name since username is None
            role=UserRole(db_user.role),
        )

    @Logger.io
    async def get_by_id(self, user_id: int) -> Optional[User]:
        db_user = await sync_to_async(UserModel.objects.filter(id=user_id).first)()
        if not db_user:
            return None
        return self._to_entity(db_user)
