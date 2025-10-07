"""Update product use case."""

from typing import Optional

from fastapi import Depends

from src.domain.entity.product_entity import Product
from src.platform.db.unit_of_work import AbstractUnitOfWork, get_unit_of_work
from src.platform.logging.loguru_io import Logger


class UpdateProductUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    @classmethod
    def depends(cls, uow: AbstractUnitOfWork = Depends(get_unit_of_work)):
        return cls(uow)

    @Logger.io
    async def update(
        self,
        product_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Product]:
        async with self.uow:
            product = await self.uow.products.get_by_id(product_id)
            if not product:
                return None

            if name is not None:
                product.name = name
            if description is not None:
                product.description = description
            if price is not None:
                product.price = price
            if is_active is not None:
                product.is_active = is_active

            updated_product = await self.uow.products.update(product)
            await self.uow.commit()

        return updated_product
