"""Order entity."""

from datetime import datetime
from typing import Optional

import attrs
from django.utils import timezone

from src.domain.enum.order_status import OrderStatus
from src.platform.exception.exceptions import DomainError
from src.platform.logging.loguru_io import Logger


@Logger.io
def validate_positive_price(instance, attribute, value):
    if value <= 0:
        raise DomainError('Price must be positive', 400)


@attrs.define
class Order:
    buyer_id: int = attrs.field(validator=attrs.validators.instance_of(int))
    seller_id: int = attrs.field(validator=attrs.validators.instance_of(int))
    product_id: int = attrs.field(validator=attrs.validators.instance_of(int))
    price: int = attrs.field(validator=[attrs.validators.instance_of(int), validate_positive_price])
    status: OrderStatus = attrs.field(
        default=OrderStatus.PENDING_PAYMENT, validator=attrs.validators.instance_of(OrderStatus)
    )
    created_at: datetime = attrs.field(factory=timezone.now)
    updated_at: datetime = attrs.field(factory=timezone.now)
    paid_at: Optional[datetime] = None
    id: Optional[int] = None

    @classmethod
    @Logger.io
    def create(cls, buyer_id: int, seller_id: int, product_id: int, price: int) -> 'Order':
        now = timezone.now()
        return cls(
            buyer_id=buyer_id,
            seller_id=seller_id,
            product_id=product_id,
            price=price,
            status=OrderStatus.PENDING_PAYMENT,
            created_at=now,
            updated_at=now,
            paid_at=None,
            id=None,
        )

    @Logger.io
    def mark_as_paid(self) -> 'Order':
        now = timezone.now()
        return attrs.evolve(self, status=OrderStatus.PAID, paid_at=now, updated_at=now)

    @Logger.io
    def cancel(self) -> 'Order':
        now = timezone.now()
        return attrs.evolve(self, status=OrderStatus.CANCELLED, updated_at=now)
