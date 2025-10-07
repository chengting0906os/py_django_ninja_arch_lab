from collections.abc import Callable
from typing import Dict, Optional

import pytest

from src.domain.entity.product_entity import Product
from src.domain.entity.user_entity import User
from test.shared.fakes import (
    FakeEmailDispatcher,
    FakeOrdersRepo,
    FakeProductsRepo,
    FakeUsersRepo,
    StubOrderUnitOfWork,
)


@pytest.fixture
def order_state():
    return {}


@pytest.fixture
def fake_users_repo_factory() -> Callable[[Dict[int, Optional[User]]], FakeUsersRepo]:
    def _factory(users: Dict[int, Optional[User]]) -> FakeUsersRepo:
        return FakeUsersRepo(users)

    return _factory


@pytest.fixture
def fake_products_repo_factory() -> Callable[
    [Dict[int, Product], Dict[int, Optional[User]]], FakeProductsRepo
]:
    def _factory(
        products: Dict[int, Product],
        sellers: Dict[int, Optional[User]],
    ) -> FakeProductsRepo:
        return FakeProductsRepo(products=products, sellers=sellers)

    return _factory


@pytest.fixture
def fake_orders_repo_factory() -> Callable[[int], FakeOrdersRepo]:
    def _factory(created_order_id: int) -> FakeOrdersRepo:
        return FakeOrdersRepo(created_order_id)

    return _factory


@pytest.fixture
def order_uow_factory() -> Callable[
    [FakeUsersRepo, FakeProductsRepo, FakeOrdersRepo], StubOrderUnitOfWork
]:
    def _factory(
        users_repo: FakeUsersRepo,
        products_repo: FakeProductsRepo,
        orders_repo: FakeOrdersRepo,
    ) -> StubOrderUnitOfWork:
        return StubOrderUnitOfWork(users_repo, products_repo, orders_repo)

    return _factory


@pytest.fixture
def fake_email_dispatcher() -> FakeEmailDispatcher:
    return FakeEmailDispatcher()
