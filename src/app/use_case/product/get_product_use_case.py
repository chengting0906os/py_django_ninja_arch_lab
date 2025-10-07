"""Get product use case."""

from typing import Optional

from fastapi import Depends

from src.domain.entity.product_entity import Product
from src.platform.db.unit_of_work import AbstractUnitOfWork, get_unit_of_work
from src.platform.logging.loguru_io import Logger


class GetProductUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    @classmethod
    def depends(cls, uow: AbstractUnitOfWork = Depends(get_unit_of_work)):
        return cls(uow)

    @Logger.io
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        async with self.uow:
            product = await self.uow.products.get_by_id(product_id)
        return product
