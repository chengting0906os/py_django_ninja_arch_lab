"""Payment use case for order management."""

import random
import string
from typing import Any, Dict

from src.app.interface.i_order_repo import IOrderRepo
from src.app.interface.i_product_repo import IProductRepo
from src.domain.enum.order_status import OrderStatus
from src.domain.enum.product_status import ProductStatus
from src.platform.exception.exceptions import DomainError, ForbiddenError, NotFoundError
from src.platform.logging.loguru_io import Logger


class MockOrderPaymentUseCase:
    def __init__(self, order_repo: IOrderRepo, product_repo: IProductRepo):
        self.order_repo = order_repo
        self.product_repo = product_repo

    # Note: transaction.atomic removed - doesn't work with async functions
    @Logger.io
    async def pay_order(self, order_id: int, buyer_id: int, card_number: str) -> Dict[str, Any]:
        order = await self.order_repo.get_by_id(order_id)
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
        updated_order = await self.order_repo.update(paid_order)
        product = await self.product_repo.get_by_id(order.product_id)
        if product:
            product.status = ProductStatus.SOLD
            await self.product_repo.update(product)
        payment_id = (
            f'PAY_MOCK_{"".join(random.choices(string.ascii_uppercase + string.digits, k=8))}'
        )

        return {
            'order_id': updated_order.id,
            'payment_id': payment_id,
            'status': 'paid',
            'paid_at': updated_order.paid_at.isoformat() if updated_order.paid_at else None,
        }
