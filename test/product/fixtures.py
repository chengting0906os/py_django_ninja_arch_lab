from collections.abc import Callable

import pytest

from src.domain.entity.product_entity import Product
from test.shared.fakes import FakeProductsRepo, StubProductUnitOfWork


@pytest.fixture
def product_state():
    return {}


@pytest.fixture
def stub_product_uow_factory() -> Callable[[Product], StubProductUnitOfWork]:
    def _factory(created_product: Product) -> StubProductUnitOfWork:
        repo = FakeProductsRepo(created_product=created_product)
        return StubProductUnitOfWork(products_repo=repo)

    return _factory
