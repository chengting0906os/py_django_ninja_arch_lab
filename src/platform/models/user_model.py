"""Custom Django user model with role support."""

from django.contrib.auth.models import AbstractUser
from django.db import models

from src.domain.enum.user_role_enum import UserRole


class User(AbstractUser):
    username = None  # type: ignore[assignment]
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        # pyrefly: ignore  # not-iterable
        choices=[(role.value, role.value) for role in UserRole],
        default=UserRole.BUYER.value,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS: list[str] = []

    class Meta:  # type: ignore[override]
        app_label = 'models'
        db_table = 'user_auth'

    def __str__(self):
        return self.email
