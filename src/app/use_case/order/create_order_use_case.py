"""Create order use case."""

from src.app.interface.i_email_dispatcher import IEmailDispatcher
from src.app.interface.i_order_repo import IOrderRepo
from src.app.interface.i_product_repo import IProductRepo
from src.app.interface.i_user_repo import IUserRepo
from src.domain.aggregate.order_aggregate import OrderAggregate
from src.domain.domain_event.order_domain_event import DomainEventProtocol, OrderCreatedEvent
from src.domain.entity.order_entity import Order
from src.platform.exception.exceptions import DomainError
from src.platform.logging.loguru_io import Logger


class CreateOrderUseCase:
    def __init__(
        self,
        email_dispatcher: IEmailDispatcher,
        user_repo: IUserRepo,
        product_repo: IProductRepo,
        order_repo: IOrderRepo,
    ):
        self.email_dispatcher = email_dispatcher
        self.user_repo = user_repo
        self.product_repo = product_repo
        self.order_repo = order_repo

    @Logger.io
    async def create_order(self, buyer_id: int, product_id: int) -> Order:
        buyer = await self.user_repo.get_by_id(buyer_id)
        if not buyer:
            raise DomainError('Buyer not found', 404)

        product, seller = await self.product_repo.get_by_id_with_seller(product_id)
        if not product:
            raise DomainError('Product not found', 404)
        if not seller:
            raise DomainError('Seller not found', 404)

        # The repository layer handles database operations
        aggregate = OrderAggregate.create_order(buyer, product, seller)
        created_order = await self.order_repo.create(aggregate.order)
        aggregate.order.id = created_order.id
        aggregate.emit_creation_events()
        events = aggregate.collect_events()
        await self._dispatch_order_events(events)

        updated_product = aggregate.get_product_for_update()
        if updated_product:
            await self.product_repo.update(updated_product)

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
