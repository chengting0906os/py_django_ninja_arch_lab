"""Product repository implementation backed by Django ORM."""

from typing import List, Optional, Tuple

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.db import transaction

from src.app.interface.i_product_repo import IProductRepo
from src.domain.entity.product_entity import Product, ProductStatus
from src.domain.entity.user_entity import User
from src.domain.enum.user_role_enum import UserRole
from src.driven_adapter.model.product_model import ProductModel
from src.platform.exception.exceptions import DomainError
from src.platform.logging.loguru_io import Logger


UserModel = get_user_model()


class ProductRepoImpl(IProductRepo):
    @staticmethod
    def _to_entity(db_product: ProductModel) -> Product:
        return Product(
            name=db_product.name,
            description=db_product.description,
            price=db_product.price,
            seller_id=db_product.seller_id,
            is_active=db_product.is_active,
            # pyrefly: ignore  # bad-argument-type
            status=ProductStatus(db_product.status),
            id=db_product.id,
        )

    @staticmethod
    def _to_user_entity(db_user: UserModel) -> User:  # type: ignore[type-arg]
        return User(
            id=db_user.id,
            email=db_user.email,
            # pyrefly: ignore  # bad-argument-type
            name=getattr(db_user, 'name', db_user.username),
            role=UserRole(db_user.role),
        )

    @Logger.io
    async def create(self, product: Product) -> Product:
        db_product = await sync_to_async(ProductModel.objects.create)(
            name=product.name,
            description=product.description,
            price=product.price,
            seller_id=product.seller_id,
            is_active=product.is_active,
            status=product.status.value,
        )
        return self._to_entity(db_product)

    @Logger.io
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        db_product = await sync_to_async(ProductModel.objects.filter(id=product_id).first)()
        return self._to_entity(db_product) if db_product else None

    @Logger.io
    async def get_by_id_with_seller(
        self, product_id: int
    ) -> Tuple[Optional[Product], Optional[User]]:
        def _fetch():
            return ProductModel.objects.select_related('seller').filter(id=product_id).first()

        db_product = await sync_to_async(_fetch)()
        if not db_product:
            return None, None
        seller_user = db_product.seller
        user_entity = self._to_user_entity(seller_user) if seller_user else None
        return self._to_entity(db_product), user_entity

    @Logger.io
    async def update(self, product: Product) -> Product:
        def _update() -> ProductModel | None:
            updated = ProductModel.objects.filter(id=product.id).update(
                name=product.name,
                description=product.description,
                price=product.price,
                is_active=product.is_active,
                status=product.status.value,
            )
            if not updated:
                return None
            return ProductModel.objects.get(id=product.id)

        db_product = await sync_to_async(_update)()
        if not db_product:
            raise ValueError(f'Product with id {product.id} not found')
        return self._to_entity(db_product)

    @Logger.io
    async def delete(self, product_id: int) -> bool:
        deleted, _ = await sync_to_async(ProductModel.objects.filter(id=product_id).delete)()
        return deleted > 0

    @Logger.io
    async def get_by_seller(self, seller_id: int) -> List[Product]:
        db_products = await sync_to_async(
            lambda: list(ProductModel.objects.filter(seller_id=seller_id).order_by('id'))
        )()
        return [self._to_entity(db_product) for db_product in db_products]

    async def list_available(self) -> List[Product]:
        db_products = await sync_to_async(
            lambda: list(
                ProductModel.objects.filter(
                    is_active=True, status=ProductStatus.AVAILABLE.value
                ).order_by('id')
            )
        )()
        return [self._to_entity(db_product) for db_product in db_products]

    @Logger.io
    async def release_product_atomically(self, product_id: int) -> Product:
        def _release() -> ProductModel:
            # pyrefly: ignore  # bad-context-manager
            with transaction.atomic():
                db_product = (
                    ProductModel.objects.select_for_update()
                    .filter(id=product_id, status=ProductStatus.RESERVED.value)
                    .first()
                )
                if not db_product:
                    raise DomainError('Unable to release product')
                db_product.status = ProductStatus.AVAILABLE.value
                db_product.save(update_fields=['status', 'updated_at'])
                return db_product

        db_product = await sync_to_async(_release)()
        return self._to_entity(db_product)
