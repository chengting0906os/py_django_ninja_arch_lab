"""List product use cases."""

from typing import List

from fastapi import Depends

from src.domain.entity.product_entity import Product
from src.platform.db.unit_of_work import AbstractUnitOfWork, get_unit_of_work
from src.platform.logging.loguru_io import Logger


class ListProductsUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    @classmethod
    def depends(cls, uow: AbstractUnitOfWork = Depends(get_unit_of_work)):
        return cls(uow)

    @Logger.io
    async def get_by_seller(self, seller_id: int) -> List[Product]:
        async with self.uow:
            products = await self.uow.products.get_by_seller(seller_id)
        return products

    @Logger.io
    async def list_available(self) -> List[Product]:
        async with self.uow:
            products = await self.uow.products.list_available()
        return products
