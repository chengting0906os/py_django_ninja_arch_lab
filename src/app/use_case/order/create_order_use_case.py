"""Create order use case."""

from fastapi import Depends

from src.domain.aggregate.order_aggregate import OrderAggregate
from src.domain.domain_event.order_domain_event import DomainEventProtocol, OrderCreatedEvent
from src.domain.entity.order_entity import Order
from src.platform.exception.exceptions import DomainError
from src.platform.logging.loguru_io import Logger
from src.platform.notification.mock_email_dispatcher import (
    MockEmailDispatcher,
    get_mock_email_dispatcher,
)
from src.platform.db.unit_of_work import AbstractUnitOfWork, get_unit_of_work
from src.app.interface.i_email_dispatcher import IEmailDispatcher


class CreateOrderUseCase:
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
    async def create_order(self, buyer_id: int, product_id: int) -> Order:
        async with self.uow:
            buyer = await self.uow.users.get_by_id(buyer_id)
            if not buyer:
                raise DomainError('Buyer not found', 404)
            # Get product and seller in one JOIN query
            product, seller = await self.uow.products.get_by_id_with_seller(product_id)
            if not product:
                raise DomainError('Product not found', 404)
            if not seller:
                raise DomainError('Seller not found', 404)

            aggregate = OrderAggregate.create_order(buyer, product, seller)
            created_order = await self.uow.orders.create(aggregate.order)
            aggregate.order.id = created_order.id
            aggregate.emit_creation_events()
            events = aggregate.collect_events()
            await self._dispatch_order_events(events)

            updated_product = aggregate.get_product_for_update()
            if updated_product:
                await self.uow.products.update(updated_product)

            await self.uow.commit()

        return created_order

    async def _dispatch_order_events(self, events: list[DomainEventProtocol]) -> None:
        for event in events:
            if not isinstance(event, OrderCreatedEvent):
                continue

            await self.email_dispatcher.send_order_confirmation(
                buyer_email=event.buyer_email,
                order_id=event.aggregate_id,
                product_name=event.product_name,
                price=event.price,
            )
            await self.email_dispatcher.notify_seller_new_order(
                seller_email=event.seller_email,
                order_id=event.aggregate_id,
                product_name=event.product_name,
                buyer_name=event.buyer_name,
                price=event.price,
            )
