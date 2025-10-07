"""Cancel order use case."""

from typing import Iterable

from fastapi import Depends

from src.app.interface.i_email_dispatcher import IEmailDispatcher
from src.domain.aggregate.order_aggregate import OrderAggregate
from src.domain.domain_event.order_domain_event import DomainEventProtocol, OrderCancelledEvent
from src.domain.enum.order_status import OrderStatus
from src.platform.db.unit_of_work import AbstractUnitOfWork, get_unit_of_work
from src.platform.exception.exceptions import DomainError, ForbiddenError, NotFoundError
from src.platform.logging.loguru_io import Logger
from src.platform.notification.mock_email_dispatcher import (
    MockEmailDispatcher,
    get_mock_email_dispatcher,
)


class CancelOrderUseCase:
    def __init__(self, uow: AbstractUnitOfWork, email_dispatcher: IEmailDispatcher):
        self.uow = uow
        self.email_dispatcher = email_dispatcher

    @classmethod
    def depends(
        cls,
        uow: AbstractUnitOfWork = Depends(get_unit_of_work),
        email_dispatcher: MockEmailDispatcher = Depends(get_mock_email_dispatcher),
    ):
        return cls(uow, email_dispatcher)

    @Logger.io
    async def cancel(self, order_id: int, buyer_id: int) -> None:
        async with self.uow:
            order = await self.uow.orders.get_by_id(order_id)
            if not order:
                raise NotFoundError('Order not found')
            if order.buyer_id != buyer_id:
                raise ForbiddenError('Only the buyer can cancel this order')
            if order.status == OrderStatus.PAID:
                raise DomainError('Cannot cancel paid order')
            if order.status == OrderStatus.CANCELLED:
                raise DomainError('Order already cancelled')

            buyer = await self.uow.users.get_by_id(buyer_id)
            if not buyer:
                raise DomainError('Buyer not found', 404)

            product = await self.uow.products.get_by_id(order.product_id)
            if not product:
                raise DomainError('Product not found', 404)

            seller = await self.uow.users.get_by_id(order.seller_id)
            if not seller:
                raise DomainError('Seller not found', 404)

            aggregate = OrderAggregate.from_existing_order(order, product, buyer, seller)
            aggregate.cancel()

            events = aggregate.collect_events()

            await self.uow.orders.update(aggregate.order)

            updated_product = aggregate.get_product_for_update()
            if updated_product:
                await self.uow.products.update(updated_product)

            await self.uow.commit()

        await self._dispatch(events)

    async def _dispatch(self, events: Iterable[DomainEventProtocol]) -> None:
        for event in events:
            if isinstance(event, OrderCancelledEvent):
                await self.email_dispatcher.send_order_cancellation(
                    buyer_email=event.buyer_email,
                    order_id=event.aggregate_id,
                    product_name=event.product_name,
                )
