"""Get order use case."""

from src.app.interface.i_order_repo import IOrderRepo
from src.domain.entity.order_entity import Order
from src.platform.exception.exceptions import NotFoundError
from src.platform.logging.loguru_io import Logger


class GetOrderUseCase:
    def __init__(self, order_repo: IOrderRepo):
        self.order_repo = order_repo

    @Logger.io
    async def get_order(self, order_id: int) -> Order:
        order = await self.order_repo.get_by_id(order_id)

        if not order:
            raise NotFoundError('Order not found')

        return order
