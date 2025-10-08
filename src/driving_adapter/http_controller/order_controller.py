"""Order controller implemented with Django Ninja Extra."""

from typing import Any, Optional

from asgiref.sync import sync_to_async
from django.http import HttpRequest
from injector import inject
from ninja_extra import ControllerBase, api_controller, http_delete, http_get, http_post

from src.app.use_case.order.cancel_order_use_case import CancelOrderUseCase
from src.app.use_case.order.create_order_use_case import CreateOrderUseCase
from src.app.use_case.order.get_order_use_case import GetOrderUseCase
from src.app.use_case.order.list_order_use_case import ListOrdersUseCase
from src.app.use_case.order.mock_order_payment_use_case import MockOrderPaymentUseCase
from src.domain.enum.user_role_enum import UserRole
from src.driving_adapter.http_controller.schema.order_schema import (
    OrderCreateRequest,
    OrderResponse,
    PaymentRequest,
    PaymentResponse,
)
from src.platform.exception.exceptions import DomainError, ForbiddenError
from src.platform.logging.loguru_io import Logger


def _build_order_response(order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        buyer_id=order.buyer_id,
        seller_id=order.seller_id,
        product_id=order.product_id,
        price=order.price,
        status=order.status.value,
        created_at=order.created_at,
        paid_at=order.paid_at,
    )


@api_controller('/order', tags=['order'])
class OrderController(ControllerBase):
    @inject
    def __init__(
        self,
        create_order_use_case: CreateOrderUseCase,
        cancel_order_use_case: CancelOrderUseCase,
        get_order_use_case: GetOrderUseCase,
        list_orders_use_case: ListOrdersUseCase,
        mock_order_payment_use_case: MockOrderPaymentUseCase,
    ):
        self.create_order_use_case = create_order_use_case
        self.cancel_order_use_case = cancel_order_use_case
        self.get_order_use_case = get_order_use_case
        self.list_orders_use_case = list_orders_use_case
        self.mock_order_payment_use_case = mock_order_payment_use_case

    async def _get_authenticated_user(self, request: HttpRequest):
        user = await sync_to_async(lambda: request.user)()
        if not user or not user.is_authenticated:
            raise ForbiddenError('Authentication required')
        return user

    async def _ensure_buyer(self, request: HttpRequest):
        user = await self._get_authenticated_user(request)
        role = getattr(user, 'role', UserRole.BUYER.value)
        if role != UserRole.BUYER.value:
            raise ForbiddenError('Only buyers can perform this action')
        return user

    @http_post('/', response={201: OrderResponse})
    @Logger.io
    async def create_order(self, request: HttpRequest, payload: OrderCreateRequest):
        buyer = await self._ensure_buyer(request)
        if buyer.id is None:
            raise DomainError('Authenticated user ID cannot be None')

        order = await self.create_order_use_case.create_order(
            buyer_id=buyer.id, product_id=payload.product_id
        )

        if order.id is None:
            raise DomainError('Order ID should not be None after creation')

        return self.create_response(_build_order_response(order), status_code=201)

    @http_get('/my-orders', response=list[dict[str, Any]])
    @Logger.io
    async def list_my_orders(self, request: HttpRequest):
        # Extract order_status from query parameters manually
        order_status_raw = request.GET.get('order_status')
        order_status: Optional[str] = str(order_status_raw) if order_status_raw else None

        user = await self._get_authenticated_user(request)
        role = getattr(user, 'role', UserRole.BUYER.value)

        if role == UserRole.BUYER.value:
            if user.id is None:
                raise DomainError('Authenticated user ID cannot be None')
            return await self.list_orders_use_case.list_buyer_orders(user.id, order_status)
        if role == UserRole.SELLER.value:
            if user.id is None:
                raise DomainError('Authenticated user ID cannot be None')
            return await self.list_orders_use_case.list_seller_orders(user.id, order_status)
        return []

    @http_get('/{order_id}', response=OrderResponse)
    @Logger.io
    async def get_order(self, request: HttpRequest, order_id: int):
        await self._get_authenticated_user(request)
        order = await self.get_order_use_case.get_order(order_id)
        return _build_order_response(order)

    @http_post('/{order_id}/pay', response=PaymentResponse)
    @Logger.io
    async def pay_order(self, request: HttpRequest, order_id: int, payload: PaymentRequest):
        buyer = await self._ensure_buyer(request)
        if buyer.id is None:
            raise DomainError('Authenticated user ID cannot be None')

        payment_result = await self.mock_order_payment_use_case.pay_order(
            order_id=order_id, buyer_id=buyer.id, card_number=payload.card_number
        )
        return PaymentResponse(**payment_result)

    @http_delete('/{order_id}', response={204: None})
    @Logger.io
    async def cancel_order(self, request: HttpRequest, order_id: int):
        buyer = await self._ensure_buyer(request)
        if buyer.id is None:
            raise DomainError('Authenticated user ID cannot be None')

        await self.cancel_order_use_case.cancel(order_id=order_id, buyer_id=buyer.id)
        return self.create_response(None, status_code=204)

    @http_get('/seller/{seller_id}', response=list[dict[str, Any]])
    @Logger.io
    async def list_seller_orders(
        self, request: HttpRequest, seller_id: int, order_status: Optional[str] = None
    ):
        await self._get_authenticated_user(request)
        return await self.list_orders_use_case.list_seller_orders(seller_id, order_status)
