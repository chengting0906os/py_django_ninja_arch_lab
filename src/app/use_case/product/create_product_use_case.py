"""Create product use case."""

from fastapi import Depends

from src.domain.entity.product_entity import Product
from src.platform.db.unit_of_work import AbstractUnitOfWork, get_unit_of_work
from src.platform.logging.loguru_io import Logger


class CreateProductUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    @classmethod
    def depends(cls, uow: AbstractUnitOfWork = Depends(get_unit_of_work)):
        return cls(uow)

    @Logger.io
    async def create(
        self,
        name: str,
        description: str,
        price: int,
        seller_id: int,
        is_active: bool = True,
    ) -> Product:
        async with self.uow:
            product = Product.create(
                name=name,
                description=description,
                price=price,
                seller_id=seller_id,
                is_active=is_active,
            )

            created_product = await self.uow.products.create(product)
            await self.uow.commit()

        return created_product
