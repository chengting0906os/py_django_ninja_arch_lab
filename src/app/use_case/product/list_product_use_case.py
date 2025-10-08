"""List product use cases."""

from typing import List

from src.app.interface.i_product_repo import IProductRepo
from src.domain.entity.product_entity import Product
from src.platform.logging.loguru_io import Logger


class ListProductUseCase:
    def __init__(self, product_repo: IProductRepo):
        self.product_repo = product_repo

    @Logger.io
    async def get_by_seller(self, seller_id: int) -> List[Product]:
        products = await self.product_repo.get_by_seller(seller_id)
        return products

    @Logger.io
    async def list_available(self) -> List[Product]:
        products = await self.product_repo.list_available()
        return products
