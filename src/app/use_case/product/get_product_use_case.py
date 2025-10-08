"""Get product use case."""

from typing import Optional

from src.app.interface.i_product_repo import IProductRepo
from src.domain.entity.product_entity import Product
from src.platform.logging.loguru_io import Logger


class GetProductUseCase:
    def __init__(self, product_repo: IProductRepo):
        self.product_repo = product_repo

    @Logger.io
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        product = await self.product_repo.get_by_id(product_id)
        return product
