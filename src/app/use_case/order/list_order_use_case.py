from typing import Any, Optional

from src.app.interface.i_order_repo import IOrderRepo
from src.platform.logging.loguru_io import Logger


class ListOrdersUseCase:
    def __init__(self, order_repo: IOrderRepo):
        self.order_repo = order_repo

    @Logger.io
    async def list_buyer_orders(
        self, buyer_id: int, status: Optional[str] = None
    ) -> list[dict[str, Any]]:
        orders = await self.order_repo.get_buyer_orders_with_details(buyer_id)
        if status:
            orders = [order for order in orders if order['status'] == status]

        return orders

    @Logger.io
    async def list_seller_orders(
        self, seller_id: int, status: Optional[str] = None
    ) -> list[dict[str, Any]]:
        orders = await self.order_repo.get_seller_orders_with_details(seller_id)

        if status:
            orders = [order for order in orders if order['status'] == status]

        return orders
