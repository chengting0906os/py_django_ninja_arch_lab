"""Order repository implementation backed by Django ORM."""

from typing import List, Optional

from asgiref.sync import sync_to_async
from django.db import transaction
from django.utils import timezone

from src.app.interface.i_order_repo import IOrderRepo
from src.domain.entity.order_entity import Order, OrderStatus
from src.platform.models.order_model import OrderModel
from src.platform.exception.exceptions import DomainError, ForbiddenError, NotFoundError
from src.platform.logging.loguru_io import Logger


class OrderRepoImpl(IOrderRepo):
    @staticmethod
    def _to_entity(db_order: OrderModel) -> Order:
        return Order(
            buyer_id=db_order.buyer_id,
            seller_id=db_order.seller_id,
            product_id=db_order.product_id,
            price=db_order.price,
            # pyrefly: ignore  # bad-argument-type
            status=OrderStatus(db_order.status),
            created_at=db_order.created_at,
            updated_at=db_order.updated_at,
            # pyrefly: ignore  # bad-argument-type
            paid_at=db_order.paid_at,
            id=db_order.id,
        )

    @Logger.io
    async def create(self, order: Order) -> Order:
        db_order = await sync_to_async(OrderModel.objects.create)(
            buyer_id=order.buyer_id,
            seller_id=order.seller_id,
            product_id=order.product_id,
            price=order.price,
            status=order.status.value,
            created_at=order.created_at,
            updated_at=order.updated_at,
            paid_at=order.paid_at,
        )
        return self._to_entity(db_order)

    @Logger.io
    async def get_by_id(self, order_id: int) -> Optional[Order]:
        db_order = await sync_to_async(OrderModel.objects.filter(id=order_id).first)()
        return self._to_entity(db_order) if db_order else None

    @Logger.io
    async def get_by_product_id(self, product_id: int) -> Optional[Order]:
        db_order = await sync_to_async(
            lambda: OrderModel.objects.filter(product_id=product_id)
            .exclude(status=OrderStatus.CANCELLED.value)
            .first()
        )()
        return self._to_entity(db_order) if db_order else None

    @Logger.io
    async def get_by_buyer(self, buyer_id: int) -> List[Order]:
        db_orders = await sync_to_async(
            lambda: list(OrderModel.objects.filter(buyer_id=buyer_id).order_by('id'))
        )()
        return [self._to_entity(db_order) for db_order in db_orders]

    @Logger.io
    async def get_by_seller(self, seller_id: int) -> List[Order]:
        db_orders = await sync_to_async(
            lambda: list(OrderModel.objects.filter(seller_id=seller_id).order_by('id'))
        )()
        return [self._to_entity(db_order) for db_order in db_orders]

    @Logger.io
    async def update(self, order: Order) -> Order:
        def _update() -> OrderModel | None:
            updated = OrderModel.objects.filter(id=order.id).update(
                buyer_id=order.buyer_id,
                seller_id=order.seller_id,
                product_id=order.product_id,
                price=order.price,
                status=order.status.value,
                updated_at=order.updated_at,
                paid_at=order.paid_at,
            )
            if not updated:
                return None
            return OrderModel.objects.get(id=order.id)

        db_order = await sync_to_async(_update)()
        if not db_order:
            raise ValueError(f'Order with id {order.id} not found')
        return self._to_entity(db_order)

    @Logger.io
    async def cancel_order_atomically(self, order_id: int, buyer_id: int) -> Order:
        def _cancel() -> OrderModel:
            # pyrefly: ignore  # bad-context-manager
            with transaction.atomic():
                db_order = (
                    OrderModel.objects.select_for_update()
                    .filter(
                        id=order_id,
                        buyer_id=buyer_id,
                        status=OrderStatus.PENDING_PAYMENT.value,
                    )
                    .first()
                )
                if not db_order:
                    existing_order = OrderModel.objects.filter(id=order_id).first()
                    if not existing_order:
                        raise NotFoundError('Order not found')
                    if existing_order.buyer_id != buyer_id:
                        raise ForbiddenError('Only the buyer can cancel this order')
                    if existing_order.status == OrderStatus.PAID.value:
                        raise DomainError('Cannot cancel paid order')
                    if existing_order.status == OrderStatus.CANCELLED.value:
                        raise DomainError('Order already cancelled')
                    raise DomainError('Unable to cancel order')
                db_order.status = OrderStatus.CANCELLED.value
                db_order.updated_at = timezone.now()
                db_order.save(update_fields=['status', 'updated_at'])
                return db_order

        db_order = await sync_to_async(_cancel)()
        return self._to_entity(db_order)

    @Logger.io
    async def get_buyer_orders_with_details(self, buyer_id: int) -> List[dict]:
        def _fetch() -> List[OrderModel]:
            return list(
                OrderModel.objects.select_related('product', 'buyer', 'seller')
                .filter(buyer_id=buyer_id)
                .order_by('id')
            )

        db_orders = await sync_to_async(_fetch)()
        return [
            {
                'id': db_order.id,
                'buyer_id': db_order.buyer_id,
                'seller_id': db_order.seller_id,
                'product_id': db_order.product_id,
                'price': db_order.price,
                'status': db_order.status,
                'created_at': db_order.created_at,
                'paid_at': db_order.paid_at,
                'product_name': getattr(db_order.product, 'name', 'Unknown Product'),
                'buyer_name': db_order.buyer.first_name or db_order.buyer.email.split('@')[0]
                if db_order.buyer
                else 'Unknown Buyer',
                'seller_name': db_order.seller.first_name or db_order.seller.email.split('@')[0]
                if db_order.seller
                else 'Unknown Seller',
            }
            for db_order in db_orders
        ]

    @Logger.io
    async def get_seller_orders_with_details(self, seller_id: int) -> List[dict]:
        def _fetch() -> List[OrderModel]:
            return list(
                OrderModel.objects.select_related('product', 'buyer', 'seller')
                .filter(seller_id=seller_id)
                .order_by('id')
            )

        db_orders = await sync_to_async(_fetch)()
        return [
            {
                'id': db_order.id,
                'buyer_id': db_order.buyer_id,
                'seller_id': db_order.seller_id,
                'product_id': db_order.product_id,
                'price': db_order.price,
                'status': db_order.status,
                'created_at': db_order.created_at,
                'paid_at': db_order.paid_at,
                'product_name': getattr(db_order.product, 'name', 'Unknown Product'),
                'buyer_name': db_order.buyer.first_name or db_order.buyer.email.split('@')[0]
                if db_order.buyer
                else 'Unknown Buyer',
                'seller_name': db_order.seller.first_name or db_order.seller.email.split('@')[0]
                if db_order.seller
                else 'Unknown Seller',
            }
            for db_order in db_orders
        ]
