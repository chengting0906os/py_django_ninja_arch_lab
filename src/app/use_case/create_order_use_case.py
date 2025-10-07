"""Create order use case."""

from fastapi import Depends

from src.domain.aggregate.order_aggregate import OrderAggregate
from src.domain.entity.order_entity import Order
from src.app.use_case.mock_send_email_use_case import MockSendEmailUseCase
from src.platform.exception.exceptions import DomainError
from src.platform.logging.loguru_io import Logger
from src.platform.notification.mock_email_dispatcher import (
    MockEmailDispatcher,
    get_mock_email_service,
)
from src.platform.db.unit_of_work import AbstractUnitOfWork, get_unit_of_work


class CreateOrderUseCase:
    def __init__(self, uow: AbstractUnitOfWork, email_service: MockEmailDispatcher):
        self.uow = uow
        self.email_service = email_service
        self.email_use_case = MockSendEmailUseCase(email_service)

    @classmethod
    def depends(
        cls,
        uow: AbstractUnitOfWork = Depends(get_unit_of_work),
        email_service: MockEmailDispatcher = Depends(get_mock_email_service),
    ):
        return cls(uow, email_service)

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
            for event in events:
                await self.email_use_case.handle_notification(event)

            updated_product = aggregate.get_product_for_update()
            if updated_product:
                await self.uow.products.update(updated_product)

            await self.uow.commit()

        return created_order
