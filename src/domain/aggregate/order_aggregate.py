"""Order Aggregate Root implementation."""

from typing import List, Optional

import attrs
from django.utils import timezone

from src.domain.domain_event.order_domain_event import (
    DomainEventProtocol,
    OrderCancelledEvent,
    OrderCreatedEvent,
    OrderPaidEvent,
    ProductReleasedEvent,
    ProductReservedEvent,
)
from src.domain.entity.order_entity import Order, OrderStatus
from src.domain.entity.product_entity import Product, ProductStatus
from src.domain.entity.user_entity import User
from src.domain.enum.user_role_enum import UserRole
from src.domain.value_object.order_value_object import BuyerInfo, ProductSnapshot, SellerInfo
from src.platform.exception.exceptions import DomainError
from src.platform.logging.loguru_io import Logger


@attrs.define
class OrderAggregate:
    order: Order
    product_snapshot: ProductSnapshot
    buyer_info: BuyerInfo
    seller_info: SellerInfo
    _events: List[DomainEventProtocol] = attrs.field(factory=list, init=False)
    _product: Optional[Product] = attrs.field(default=None, init=False)

    @classmethod
    @Logger.io
    def create_order(
        cls,
        buyer: 'User',
        product: Product,
        seller: 'User',
    ) -> 'OrderAggregate':
        if buyer.role != UserRole.BUYER.value:
            raise DomainError('Only buyers can create orders', 403)
        if buyer.id == product.seller_id:
            raise DomainError('Cannot buy your own product', 403)
        if not product.is_active:
            raise DomainError('Product not active', 400)
        if product.status != ProductStatus.AVAILABLE:
            raise DomainError('Product not available', 400)

        order = Order.create(
            buyer_id=buyer.id,
            seller_id=product.seller_id,
            product_id=product.id or 0,
            price=product.price,
        )
        product_snapshot = ProductSnapshot.from_product(product)
        buyer_info = BuyerInfo.from_user(buyer)
        seller_info = SellerInfo.from_user(seller)
        aggregate = cls(
            order=order,
            product_snapshot=product_snapshot,
            buyer_info=buyer_info,
            seller_info=seller_info,
        )
        aggregate._product = product
        aggregate._reserve_product()

        return aggregate

    @classmethod
    @Logger.io
    def from_existing_order(
        cls,
        order: Order,
        product: Product,
        buyer: 'User',
        seller: 'User',
    ) -> 'OrderAggregate':
        aggregate = cls(
            order=order,
            product_snapshot=ProductSnapshot.from_product(product),
            buyer_info=BuyerInfo.from_user(buyer),
            seller_info=SellerInfo.from_user(seller),
        )
        aggregate._product = product
        return aggregate

    def emit_creation_events(self) -> None:
        if not self.order.id:
            raise ValueError('Order must have an ID before emitting events')

        self._add_event(
            OrderCreatedEvent(
                aggregate_id=self.order.id,
                buyer_id=self.order.buyer_id,
                seller_id=self.order.seller_id,
                product_id=self.order.product_id,
                price=self.order.price,
                buyer_email=self.buyer_info.email,
                buyer_name=self.buyer_info.name,
                seller_email=self.seller_info.email,
                seller_name=self.seller_info.name,
                product_name=self.product_snapshot.name,
            )
        )

        if self._product and self._product.status == ProductStatus.RESERVED:
            self._add_event(
                ProductReservedEvent(
                    aggregate_id=self.order.id,
                    product_id=self._product.id or 0,
                    order_id=self.order.id,
                )
            )

    @Logger.io
    def process_payment(self) -> None:
        if self.order.status != OrderStatus.PENDING_PAYMENT:
            if self.order.status == OrderStatus.PAID:
                raise DomainError('Order already paid', 400)
            elif self.order.status == OrderStatus.CANCELLED:
                raise DomainError('Cannot pay for cancelled order', 400)
            else:
                raise DomainError('Invalid order status for payment', 400)

        self.order = self.order.mark_as_paid()
        if self._product:
            self._product.status = ProductStatus.SOLD

        self._add_event(
            OrderPaidEvent(
                aggregate_id=self.order.id or 0,
                buyer_id=self.order.buyer_id,
                product_id=self.order.product_id,
                paid_at=self.order.paid_at or timezone.now(),
                buyer_email=self.buyer_info.email,
                product_name=self.product_snapshot.name,
                paid_amount=self.order.price,
            )
        )

    @Logger.io
    def cancel(self) -> None:
        if self.order.status == OrderStatus.PAID:
            raise DomainError('Cannot cancel paid order', 400)
        if self.order.status == OrderStatus.CANCELLED:
            raise DomainError('Order already cancelled', 400)
        self.order = self.order.cancel()
        if self._product and self._product.status == ProductStatus.RESERVED:
            self._release_product()

        self._add_event(
            OrderCancelledEvent(
                aggregate_id=self.order.id or 0,
                buyer_id=self.order.buyer_id,
                product_id=self.order.product_id,
                buyer_email=self.buyer_info.email,
                product_name=self.product_snapshot.name,
            )
        )

    @Logger.io
    def _reserve_product(self) -> None:
        if self._product:
            self._product.status = ProductStatus.RESERVED

    @Logger.io
    def _release_product(self) -> None:
        if self._product:
            self._product.status = ProductStatus.AVAILABLE

            self._add_event(
                ProductReleasedEvent(
                    aggregate_id=self.order.id or 0,
                    product_id=self._product.id or 0,
                    order_id=self.order.id or 0,
                )
            )

    def _add_event(self, event: DomainEventProtocol) -> None:
        self._events.append(event)

    @Logger.io
    def collect_events(self) -> List[DomainEventProtocol]:
        events = self._events.copy()
        self._events.clear()
        return events

    @Logger.io
    def get_product_for_update(self) -> Optional[Product]:
        return self._product
