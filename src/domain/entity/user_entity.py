"""Domain entity definitions for user aggregate."""

from __future__ import annotations

import attrs

from src.domain.enum.user_role_enum import UserRole


# attrs.define generates an attrs-based class with optional slot-based storage for efficiency.
@attrs.define
class User:
    """User aggregate root with role awareness."""

    id: int
    email: str
    name: str  # Optional: defaults to email in repo implementation
    role: UserRole
