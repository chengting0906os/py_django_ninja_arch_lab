from typing import Dict, List, Optional, Tuple, cast

from attrs import evolve

from src.app.interface.i_email_dispatcher import IEmailDispatcher
from src.domain.entity.order_entity import Order
from src.domain.entity.product_entity import Product
from src.domain.entity.user_entity import User


class FakeProductsRepo:
    """Flexible fake repo supporting both create and lookup behaviours."""

    def __init__(
        self,
        *,
        created_product: Product | None = None,
        products: Dict[int, Product] | None = None,
        products_by_id: Dict[int, Product] | None = None,
        sellers: Dict[int, Optional[User]] | None = None,
    ):
        self._created_product = created_product
        self._products = products or {}
        self._products_by_id = products_by_id or {}
        self._sellers = sellers or {}
        self.received_product: Product | None = None
        self.requested_product_ids: List[int] = []
        self.updated_products: List[Product] = []
        self.deleted_ids: List[int] = []

    async def create(self, product: Product) -> Product:
        self.received_product = product
        return cast(Product, self._created_product)

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        return self._products_by_id.get(product_id)

    async def get_by_id_with_seller(
        self, product_id: int
    ) -> Tuple[Optional[Product], Optional[User]]:
        self.requested_product_ids.append(product_id)
        return self._products.get(product_id), self._sellers.get(product_id)

    async def update(self, product: Product) -> Product:
        self.updated_products.append(product)
        return product

    async def delete(self, product_id: int) -> bool:
        self.deleted_ids.append(product_id)
        return self._products_by_id.pop(product_id, None) is not None


class FakeOrdersRepo:
    def __init__(self, created_order_id: int):
        self.created_order_id = created_order_id
        self.created_orders: List[Order] = []

    async def create(self, order: Order) -> Order:
        stored = evolve(order, id=self.created_order_id)
        self.created_orders.append(stored)
        return stored


class FakeUsersRepo:
    def __init__(self, users: Dict[int, Optional[User]]):
        self._users = users
        self.requested_ids: List[int] = []

    async def get_by_id(self, user_id: int) -> Optional[User]:
        self.requested_ids.append(user_id)
        return self._users.get(user_id)


class FakeEmailDispatcher(IEmailDispatcher):
    def __init__(self):
        self.order_confirmation_calls: List[dict] = []
        self.notify_seller_calls: List[dict] = []

    async def send_email(self, to: str, subject: str, body: str, cc=None) -> bool:
        return True

    async def send_order_confirmation(
        self, buyer_email: str, order_id: int, product_name: str, price: int
    ) -> None:
        self.order_confirmation_calls.append(
            {
                'buyer_email': buyer_email,
                'order_id': order_id,
                'product_name': product_name,
                'price': price,
            }
        )

    async def send_payment_confirmation(
        self, buyer_email: str, order_id: int, product_name: str, paid_amount: int
    ) -> None:
        pass

    async def send_order_cancellation(
        self, buyer_email: str, order_id: int, product_name: str
    ) -> None:
        pass

    async def notify_seller_new_order(
        self, seller_email: str, order_id: int, product_name: str, buyer_name: str, price: int
    ) -> None:
        self.notify_seller_calls.append(
            {
                'seller_email': seller_email,
                'order_id': order_id,
                'product_name': product_name,
                'buyer_name': buyer_name,
                'price': price,
            }
        )
