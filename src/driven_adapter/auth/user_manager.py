"""User manager for FastAPI Users integration (infrastructure layer)."""

from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin

from src.platform.config.core_setting import settings
from src.platform.logging.loguru_io import Logger
from src.driven_adapter.model.user_model import User
from src.driven_adapter.repo.get_user_db import get_user_db


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.RESET_PASSWORD_TOKEN_SECRET.get_secret_value()
    verification_token_secret = settings.VERIFICATION_TOKEN_SECRET.get_secret_value()

    @Logger.io
    # pyrefly: ignore  # bad-override
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """Hook called after successful user registration."""

    # pyrefly: ignore  # bad-override
    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Hook called after a forgot password request."""

    # pyrefly: ignore  # bad-override
    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Hook called after requesting email verification."""


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db=user_db)
