"""Product controller implemented with Django Ninja Extra."""

from typing import List

from asgiref.sync import sync_to_async
from django.http import HttpRequest
from injector import Injector
from ninja_extra import (
    ControllerBase,
    api_controller,
    http_delete,
    http_get,
    http_patch,
    http_post,
)

from src.app.use_case.product.create_product_use_case import CreateProductUseCase
from src.app.use_case.product.delete_product_use_case import DeleteProductUseCase
from src.app.use_case.product.get_product_use_case import GetProductUseCase
from src.app.use_case.product.list_product_use_case import ListProductUseCase
from src.app.use_case.product.update_product_use_case import UpdateProductUseCase
from src.domain.enum.user_role_enum import UserRole
from src.driving_adapter.http_controller.schema.product_schema import (
    ProductCreateRequest,
    ProductResponse,
    ProductUpdateRequest,
)
from src.platform.di import ApplicationModule
from src.platform.exception.exceptions import DomainError, ForbiddenError, NotFoundError
from src.platform.logging.loguru_io import Logger


def _build_product_response(product) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        seller_id=product.seller_id,
        is_active=product.is_active,
        status=product.status.value,
    )


@api_controller('/product', tags=['product'])
class ProductController(ControllerBase):
    _injector = Injector([ApplicationModule()])

    def __init__(self):
        self.create_product_use_case = self._injector.get(CreateProductUseCase)
        self.delete_product_use_case = self._injector.get(DeleteProductUseCase)
        self.get_product_use_case = self._injector.get(GetProductUseCase)
        self.list_product_use_case = self._injector.get(ListProductUseCase)
        self.update_product_use_case = self._injector.get(UpdateProductUseCase)

    async def _get_authenticated_user(self, request: HttpRequest):
        user = await sync_to_async(lambda: request.user)()
        if not user or not user.is_authenticated:
            raise ForbiddenError('Authentication required')
        return user

    async def _ensure_seller(self, request: HttpRequest):
        user = await self._get_authenticated_user(request)
        role = getattr(user, 'role', UserRole.BUYER.value)
        if role != UserRole.SELLER.value:
            raise ForbiddenError('Only sellers can perform this action')
        return user

    @http_post('/', response={201: ProductResponse})
    @Logger.io
    async def create_product(self, request: HttpRequest, payload: ProductCreateRequest):
        seller = await self._ensure_seller(request)
        if seller.id is None:
            raise DomainError('Authenticated user ID cannot be None')

        product = await self.create_product_use_case.create(
            name=payload.name,
            description=payload.description,
            price=payload.price,
            seller_id=seller.id,
            is_active=payload.is_active,
        )

        if product.id is None:
            raise DomainError('Product ID should not be None after creation')

        return self.create_response(_build_product_response(product), status_code=201)

    @http_patch('/{product_id}', response=ProductResponse)
    @Logger.io
    async def update_product(
        self,
        request: HttpRequest,
        product_id: int,
        payload: ProductUpdateRequest,
    ):
        seller = await self._ensure_seller(request)
        # Ensure ownership before performing update
        existing = await self.get_product_use_case.get_by_id(product_id)
        if not existing:
            raise NotFoundError(f'Product with id {product_id} not found')
        if existing.seller_id != seller.id:
            raise ForbiddenError('You can only update your own products')

        product = await self.update_product_use_case.update(
            product_id=product_id,
            name=payload.name,
            description=payload.description,
            price=payload.price,
            is_active=payload.is_active,
        )

        return _build_product_response(product)

    @http_delete('/{product_id}', response={204: None})
    @Logger.io
    async def delete_product(self, request: HttpRequest, product_id: int):
        seller = await self._ensure_seller(request)
        product = await self.get_product_use_case.get_by_id(product_id)
        if not product:
            raise NotFoundError(f'Product with id {product_id} not found')
        if product.seller_id != seller.id:
            raise ForbiddenError('You can only delete your own products')

        await self.delete_product_use_case.delete(product_id)
        # Delete use case already enforces ownership; ensure record existed
        return self.create_response(None, status_code=204)

    @http_get('/{product_id}', response=ProductResponse)
    @Logger.io
    async def get_product(self, product_id: int):
        product = await self.get_product_use_case.get_by_id(product_id)

        if not product:
            raise NotFoundError(f'Product with id {product_id} not found')

        return _build_product_response(product)

    @http_get('/', response=List[ProductResponse])
    @Logger.io
    async def list_products(self, request: HttpRequest):
        # Extract seller_id from query parameters manually
        seller_id = request.GET.get('seller_id')
        if seller_id:
            # pyrefly: ignore  # no-matching-overload
            seller_id = int(seller_id)

        if seller_id is not None:
            # pyrefly: ignore  # bad-argument-type
            products = await self.list_product_use_case.get_by_seller(seller_id)
        else:
            products = await self.list_product_use_case.list_available()

        return [_build_product_response(product) for product in products if product.id is not None]
