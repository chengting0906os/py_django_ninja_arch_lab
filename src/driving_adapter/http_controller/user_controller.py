"""User controller wired with Django Ninja Extra session auth."""

from typing import Any, List

from django.contrib.auth import alogout, get_user_model
from django.http import HttpRequest, HttpResponse
from ninja_extra import ControllerBase, api_controller, http_delete, http_get, http_post, http_put

from src.domain.enum.user_role_enum import UserRole
from src.driving_adapter.http_controller.schema.user_schema import (
    ErrorResponse,
    IdOut,
    UpdatePasswordIn,
    UserIn,
    UserLoginIn,
    UserOut,
)
from src.platform.exception.exceptions import DomainError
from src.platform.logging.loguru_io import Logger


"""
Django Ninja Extra [ControllerBase]: https://eadwincode.github.io/django-ninja-extra/api_controller/
[django.contrib.auth]: https://docs.djangoproject.com/en/5.1/ref/contrib/auth/
Ninja Extra [Authentication]: https://django-ninja.dev/guides/authentication/
Django Ninja Extra [Authentication]: https://eadwincode.github.io/django-ninja-extra/tutorial/authentication/
Django Ninja Extra [Permissions]: https://eadwincode.github.io/django-ninja-extra/api_controller/api_controller_permission/
"""


UserModel = get_user_model()


def build_user_out(user: UserModel) -> UserOut:  # type: ignore[type-arg]
    return UserOut(
        id=user.id,
        username=user.email,
        name=user.email,
        email=user.email,
        role=user.role,
        is_superuser=user.is_superuser,
    )


@api_controller('/user', tags=['user'])
class UserController(ControllerBase):
    @http_get('/{id}', response={200: UserOut, 404: ErrorResponse})
    @Logger.io
    def retrieve_user(self, id: int) -> UserOut:
        user = self.get_object_or_exception(UserModel, id=id)
        return build_user_out(user)

    @http_get('/', response={200: List[UserOut], 404: ErrorResponse})
    @Logger.io
    def list_user(self) -> List[UserOut]:
        users = list(UserModel.objects.all())
        return [build_user_out(user) for user in users]

    @http_post('/', response={201: UserOut, 400: ErrorResponse})
    @Logger.io
    async def create_user(self, payload: UserIn) -> UserOut | HttpResponse:
        from asgiref.sync import sync_to_async
        from django.contrib.auth.models import Group

        if await sync_to_async(UserModel.objects.filter(email=payload.email).exists)():
            raise DomainError('Email has been existed')

        # pyrefly: ignore  # not-iterable
        if payload.role not in {role.value for role in UserRole}:
            raise DomainError('Invalid role')

        user = await sync_to_async(UserModel.objects.create)(
            email=payload.email,
            role=payload.role,
        )
        user.set_password(payload.password)
        await sync_to_async(user.save)()

        # Add user to corresponding group based on role
        group, _ = await sync_to_async(Group.objects.get_or_create)(name=payload.role)
        await sync_to_async(user.groups.add)(group)

        return self.create_response(build_user_out(user), status_code=201)

    @http_post('/login/', response={200: UserOut, 400: ErrorResponse})
    @Logger.io
    async def login_user(
        self, request: HttpRequest, payload: UserLoginIn
    ) -> UserOut | HttpResponse:
        from asgiref.sync import sync_to_async
        from django.contrib.auth import authenticate, login

        Logger.base.debug(
            f'login payload email={payload.email!r} password_len={len(payload.password) if payload.password else 0}'
        )
        if not payload.email or not payload.password:
            raise DomainError('LOGIN_BAD_CREDENTIALS')

        user = await sync_to_async(authenticate)(
            request, email=payload.email, password=payload.password
        )
        if user is None:
            raise DomainError('LOGIN_BAD_CREDENTIALS')

        await sync_to_async(login)(request, user)

        return self.create_response(build_user_out(user), status_code=200)

    @http_post('/logout/', response={200: Any, 400: ErrorResponse})
    @Logger.io
    async def logout_user(self, request: HttpRequest) -> HttpResponse:
        await alogout(request)
        return self.create_response({'success': True}, status_code=200)

    @http_put('/{id}', response={200: IdOut, 400: ErrorResponse})
    @Logger.io
    def update_user_password(self, id: int, payload: UpdatePasswordIn) -> IdOut | HttpResponse:
        user = self.get_object_or_exception(UserModel, id=id)
        user.set_password(payload.password)
        user.save()
        return self.create_response(IdOut(id=id), status_code=200)

    @http_delete('/{id}', response={200: IdOut, 400: ErrorResponse})
    @Logger.io
    def delete_user(self, id: int) -> HttpResponse:
        self.get_object_or_exception(UserModel, id=id)
        UserModel.objects.filter(id=id).delete()
        return self.create_response(IdOut(id=id), status_code=200)
