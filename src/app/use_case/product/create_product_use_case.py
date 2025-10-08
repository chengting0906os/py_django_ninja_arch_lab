"""Create product use case."""

from src.app.interface.i_product_repo import IProductRepo
from src.domain.entity.product_entity import Product
from src.platform.logging.loguru_io import Logger


class CreateProductUseCase:
    def __init__(self, product_repo: IProductRepo):
        self.product_repo = product_repo

    @Logger.io
    async def create(
        self,
        name: str,
        description: str,
        price: int,
        seller_id: int,
        is_active: bool = True,
    ) -> Product:
        product = Product.create(
            name=name,
            description=description,
            price=price,
            seller_id=seller_id,
            is_active=is_active,
        )

        created_product = await self.product_repo.create(product)
        return created_product
