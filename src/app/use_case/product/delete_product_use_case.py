"""Delete product use case."""

from fastapi import Depends

from src.domain.enum.product_status import ProductStatus
from src.platform.db.unit_of_work import AbstractUnitOfWork, get_unit_of_work
from src.platform.logging.loguru_io import Logger


class DeleteProductUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    @classmethod
    def depends(cls, uow: AbstractUnitOfWork = Depends(get_unit_of_work)):
        return cls(uow)

    @Logger.io
    async def delete(self, product_id: int) -> bool:
        async with self.uow:
            product = await self.uow.products.get_by_id(product_id)
            if not product:
                return False

            if product.status == ProductStatus.RESERVED:
                raise ValueError('Cannot delete reserved product')
            if product.status == ProductStatus.SOLD:
                raise ValueError('Cannot delete sold product')

            deleted = await self.uow.products.delete(product_id)
            await self.uow.commit()

        return deleted
