from typing import cast

import pytest

from src.app.use_case.order.create_order_use_case import CreateOrderUseCase
from src.domain.entity.product_entity import Product
from src.domain.entity.user_entity import User
from src.domain.enum.product_status import ProductStatus
from src.domain.enum.user_role_enum import UserRole
from src.platform.db.unit_of_work import AbstractUnitOfWork
from src.platform.exception.exceptions import DomainError


def _build_product(name: str, seller_id: int, price: int, is_active: bool = True) -> Product:
    product = Product.create(
        name=name,
        description=f'{name} description',
        price=price,
        seller_id=seller_id,
        is_active=is_active,
    )
    product.id = 100
    return product


def _build_user(user_id: int, email: str, name: str, role: UserRole) -> User:
    return User(id=user_id, email=email, name=name, role=role)


@pytest.mark.asyncio
async def test_create_order_successfully_reserves_product_and_sends_emails(
    fake_users_repo_factory,
    fake_products_repo_factory,
    fake_orders_repo_factory,
    order_uow_factory,
    fake_email_dispatcher,
):
    # given
    buyer = _build_user(1, 'buyer@example.com', 'Buyer One', UserRole.BUYER)
    seller = _build_user(2, 'seller@example.com', 'Seller One', UserRole.SELLER)
    product = _build_product('Test Product', seller_id=seller.id, price=500)

    users_repo = fake_users_repo_factory({buyer.id: buyer})
    products_repo = fake_products_repo_factory({product.id: product}, {product.id: seller})
    orders_repo = fake_orders_repo_factory(created_order_id=55)
    uow = order_uow_factory(users_repo, products_repo, orders_repo)
    use_case = CreateOrderUseCase(
        uow=cast(AbstractUnitOfWork, uow),
        email_dispatcher=fake_email_dispatcher,
    )

    # when
    result = await use_case.create_order(buyer_id=buyer.id, product_id=product.id or 0)

    # then
    assert result.id == 55
    assert orders_repo.created_orders, 'Order repository should receive a new order'
    created_order = orders_repo.created_orders[0]
    assert created_order.buyer_id == buyer.id
    assert created_order.product_id == product.id
    assert uow.commit_called
    assert products_repo.updated_products
    assert products_repo.updated_products[0].status == ProductStatus.RESERVED
    assert fake_email_dispatcher.order_confirmation_calls == [
        {
            'buyer_email': buyer.email,
            'order_id': 55,
            'product_name': product.name,
            'price': product.price,
        }
    ]
    assert fake_email_dispatcher.notify_seller_calls == [
        {
            'seller_email': seller.email,
            'order_id': 55,
            'product_name': product.name,
            'buyer_name': buyer.name,
            'price': product.price,
        }
    ]


@pytest.mark.asyncio
async def test_create_order_raises_when_buyer_missing(
    fake_users_repo_factory,
    fake_products_repo_factory,
    fake_orders_repo_factory,
    order_uow_factory,
    fake_email_dispatcher,
):
    # given
    seller = _build_user(2, 'seller@example.com', 'Seller One', UserRole.SELLER)
    product = _build_product('Test Product', seller_id=seller.id, price=500)

    users_repo = fake_users_repo_factory({})  # Buyer not found
    products_repo = fake_products_repo_factory({product.id: product}, {product.id: seller})
    orders_repo = fake_orders_repo_factory(created_order_id=55)
    uow = order_uow_factory(users_repo, products_repo, orders_repo)
    use_case = CreateOrderUseCase(
        uow=cast(AbstractUnitOfWork, uow),
        email_dispatcher=fake_email_dispatcher,
    )

    # when
    with pytest.raises(DomainError) as exc_info:
        await use_case.create_order(buyer_id=1, product_id=product.id or 0)

    # then
    assert 'Buyer not found' in str(exc_info.value)
    assert not orders_repo.created_orders
    assert not uow.commit_called
