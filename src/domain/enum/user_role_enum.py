"""User models."""

from enum import StrEnum


class UserRole(StrEnum):
    SELLER = 'seller'
    BUYER = 'buyer'
