"""Payment use case for order management."""

import random
import string
from typing import Any, Dict

from fastapi import Depends

from src.domain.enum.order_status import OrderStatus
from src.domain.enum.product_status import ProductStatus
from src.platform.db.unit_of_work import AbstractUnitOfWork, get_unit_of_work
from src.platform.exception.exceptions import DomainError, ForbiddenError, NotFoundError
from src.platform.logging.loguru_io import Logger


class MockOrderPaymentUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    @classmethod
    def depends(cls, uow: AbstractUnitOfWork = Depends(get_unit_of_work)):
        return cls(uow=uow)

    @Logger.io
    async def pay_order(self, order_id: int, buyer_id: int, card_number: str) -> Dict[str, Any]:
        async with self.uow:
            order = await self.uow.orders.get_by_id(order_id)
            if not order:
                raise NotFoundError('Order not found')
            if order.buyer_id != buyer_id:
                raise ForbiddenError('Only the buyer can pay for this order')
            if order.status == OrderStatus.PAID:
                raise DomainError('Order already paid')
            elif order.status == OrderStatus.CANCELLED:
                raise DomainError('Cannot pay for cancelled order')
            elif order.status != OrderStatus.PENDING_PAYMENT:
                raise DomainError('Order is not in a payable state')

            paid_order = order.mark_as_paid()
            updated_order = await self.uow.orders.update(paid_order)
            product = await self.uow.products.get_by_id(order.product_id)
            if product:
                product.status = ProductStatus.SOLD
                await self.uow.products.update(product)
            payment_id = (
                f'PAY_MOCK_{"".join(random.choices(string.ascii_uppercase + string.digits, k=8))}'
            )
            await self.uow.commit()

            return {
                'order_id': updated_order.id,
                'payment_id': payment_id,
                'status': 'paid',
                'paid_at': updated_order.paid_at.isoformat() if updated_order.paid_at else None,
            }
