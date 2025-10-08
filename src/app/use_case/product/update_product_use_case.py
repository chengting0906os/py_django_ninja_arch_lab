"""Update product use case."""

from typing import Optional

from src.app.interface.i_product_repo import IProductRepo
from src.domain.entity.product_entity import Product
from src.platform.logging.loguru_io import Logger


class UpdateProductUseCase:
    def __init__(self, product_repo: IProductRepo):
        self.product_repo = product_repo

    @Logger.io
    async def update(
        self,
        product_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Product]:
        product = await self.product_repo.get_by_id(product_id)
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

        updated_product = await self.product_repo.update(product)
        return updated_product
