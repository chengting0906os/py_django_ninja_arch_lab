"""Django Ninja permissions based on Django groups."""

from django.http import HttpRequest
from ninja_extra.permissions import BasePermission

from src.platform.exception.exceptions import ForbiddenError


class IsAuthenticated(BasePermission):
    """Permission to check if user is authenticated."""

    def has_permission(self, request: HttpRequest, controller) -> bool:
        if not request.user or not request.user.is_authenticated:
            raise ForbiddenError('Authentication required')
        return True


class IsBuyer(BasePermission):
    """Permission to check if user is in buyer group."""

    def has_permission(self, request: HttpRequest, controller) -> bool:
        if not request.user or not request.user.is_authenticated:
            raise ForbiddenError('Authentication required')
        if not request.user.groups.filter(name='buyer').exists():
            raise ForbiddenError('Only buyers can perform this action')
        return True


class IsSeller(BasePermission):
    """Permission to check if user is in seller group."""

    def has_permission(self, request: HttpRequest, controller) -> bool:
        if not request.user or not request.user.is_authenticated:
            raise ForbiddenError('Authentication required')
        if not request.user.groups.filter(name='seller').exists():
            raise ForbiddenError('Only sellers can perform this action')
        return True
