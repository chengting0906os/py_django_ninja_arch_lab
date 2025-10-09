"""Centralized exception handlers for Django Ninja Extra."""

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse
from ninja.errors import ValidationError
from ninja_extra import NinjaExtraAPI

from src.platform.exception.exceptions import DomainError
from src.platform.logging.loguru_io import Logger


class ExecFailError(Exception):
    """Base exception for execution failures."""


class FileNotExsitsError(Exception):
    """Raised when a required file is missing."""


class InvalidActionRequestError(Exception):
    """Raised when an invalid action is requested."""


class SSHConnectionError(Exception):
    """Raised when SSH connection fails."""


class EntityNotFoundError(ExecFailError):
    """Raised when an entity is not found."""


class PermissionDeniedError(ExecFailError):
    """Raised when user lacks permission for an action."""


class BadRequestError(ExecFailError):
    """Raised for bad request errors."""


def setup_exception_handlers(api_instance: NinjaExtraAPI) -> None:
    """Register global exception handlers on the provided API instance."""

    @api_instance.exception_handler(DomainError)
    def domain_error_handler(request: HttpRequest, exc: DomainError) -> HttpResponse:
        if exc.status_code >= 500:
            Logger.base.exception(f'Domain error: {exc.message}')
        else:
            Logger.base.warning(f'Domain error: {exc.message}')
        return api_instance.create_response(
            request, {'detail': exc.message}, status=exc.status_code
        )

    @api_instance.exception_handler(EntityNotFoundError)
    def entity_not_found_error_handler(
        request: HttpRequest, exc: EntityNotFoundError
    ) -> HttpResponse:
        message = str(exc) or 'Entity not found'
        return api_instance.create_response(request, {'detail': message}, status=404)

    @api_instance.exception_handler(PermissionDeniedError)
    def permission_denied_error_handler(
        request: HttpRequest, exc: PermissionDeniedError
    ) -> HttpResponse:
        message = str(exc) or 'Permission denied'
        return api_instance.create_response(request, {'detail': message}, status=403)

    @api_instance.exception_handler(ExecFailError)
    def execute_failed_error_handler(request: HttpRequest, exc: ExecFailError) -> HttpResponse:
        message = str(exc) or 'Execution failed'
        return api_instance.create_response(request, {'detail': message}, status=400)

    @api_instance.exception_handler(IntegrityError)
    def integrity_error_handler(request: HttpRequest, exc: IntegrityError) -> HttpResponse:
        detail = 'Database integrity error'
        error_text = str(exc)
        if 'FOREIGN KEY' in error_text:
            detail = 'Foreign key constraint failed'
        elif 'Duplicate entry' in error_text or 'unique constraint' in error_text.lower():
            detail = 'Duplicate entry'
        return api_instance.create_response(request, {'detail': detail}, status=400)

    @api_instance.exception_handler(ObjectDoesNotExist)
    def object_does_not_exist_handler(
        request: HttpRequest, exc: ObjectDoesNotExist
    ) -> HttpResponse:
        return api_instance.create_response(request, {'detail': 'Resource not found'}, status=404)

    @api_instance.exception_handler(ValueError)
    def value_error_handler(request: HttpRequest, exc: ValueError) -> HttpResponse:
        return api_instance.create_response(request, {'detail': str(exc)}, status=400)

    @api_instance.exception_handler(ValidationError)
    def validation_error_handler(request: HttpRequest, exc: ValidationError) -> HttpResponse:
        """Normalize Ninja schema validation errors to 400 Bad Request."""
        return api_instance.create_response(request, {'detail': 'Validation error'}, status=400)

    @api_instance.exception_handler(Exception)
    def exception_error_handler(request: HttpRequest, exc: Exception) -> HttpResponse:
        Logger.base.exception(f'Unhandled exception: {exc}')
        return api_instance.create_response(
            request, {'detail': 'Internal Server Error'}, status=500
        )
