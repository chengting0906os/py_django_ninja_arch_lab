"""Delete product use case."""

from src.app.interface.i_product_repo import IProductRepo
from src.domain.enum.product_status import ProductStatus
from src.platform.logging.loguru_io import Logger


class DeleteProductUseCase:
    def __init__(self, product_repo: IProductRepo):
        self.product_repo = product_repo

    @Logger.io
    async def delete(self, product_id: int) -> bool:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            return False

        if product.status == ProductStatus.RESERVED:
            raise ValueError('Cannot delete reserved product')
        if product.status == ProductStatus.SOLD:
            raise ValueError('Cannot delete sold product')

        deleted = await self.product_repo.delete(product_id)
        return deleted
