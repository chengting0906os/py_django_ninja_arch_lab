"""Cancel order use case."""

from typing import Iterable

from src.app.interface.i_email_dispatcher import IEmailDispatcher
from src.app.interface.i_order_repo import IOrderRepo
from src.app.interface.i_product_repo import IProductRepo
from src.app.interface.i_user_repo import IUserRepo
from src.domain.aggregate.order_aggregate import OrderAggregate
from src.domain.domain_event.order_domain_event import DomainEventProtocol, OrderCancelledEvent
from src.domain.enum.order_status import OrderStatus
from src.platform.exception.exceptions import DomainError, ForbiddenError, NotFoundError
from src.platform.logging.loguru_io import Logger


class CancelOrderUseCase:
    def __init__(
        self,
        email_dispatcher: IEmailDispatcher,
        user_repo: IUserRepo,
        product_repo: IProductRepo,
        order_repo: IOrderRepo,
    ):
        self.email_dispatcher = email_dispatcher
        self.order_repo = order_repo
        self.user_repo = user_repo
        self.product_repo = product_repo

    # Note: transaction.atomic removed - doesn't work with async functions
    @Logger.io
    async def cancel(self, order_id: int, buyer_id: int) -> None:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundError('Order not found')
        if order.buyer_id != buyer_id:
            raise ForbiddenError('Only the buyer can cancel this order')
        if order.status == OrderStatus.PAID:
            raise DomainError('Cannot cancel paid order')
        if order.status == OrderStatus.CANCELLED:
            raise DomainError('Order already cancelled')

        buyer = await self.user_repo.get_by_id(buyer_id)
        if not buyer:
            raise DomainError('Buyer not found', 404)

        product = await self.product_repo.get_by_id(order.product_id)
        if not product:
            raise DomainError('Product not found', 404)

        seller = await self.user_repo.get_by_id(order.seller_id)
        if not seller:
            raise DomainError('Seller not found', 404)

        aggregate = OrderAggregate.from_existing_order(order, product, buyer, seller)
        aggregate.cancel()

        events = aggregate.collect_events()

        await self.order_repo.update(aggregate.order)

        updated_product = aggregate.get_product_for_update()
        if updated_product:
            await self.product_repo.update(updated_product)

        await self._dispatch(events)

    async def _dispatch(self, events: Iterable[DomainEventProtocol]) -> None:
        for event in events:
            if isinstance(event, OrderCancelledEvent):
                await self.email_dispatcher.send_order_cancellation(
                    buyer_email=event.buyer_email,
                    order_id=event.aggregate_id,
                    product_name=event.product_name,
                )
