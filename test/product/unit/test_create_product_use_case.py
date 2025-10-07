from typing import TypedDict, cast

import pytest
from attrs import evolve

from src.app.use_case.product.create_product_use_case import CreateProductUseCase
from src.domain.entity.product_entity import Product
from src.platform.db.unit_of_work import AbstractUnitOfWork
from test.shared.fakes import StubProductUnitOfWork


class ProductInput(TypedDict):
    name: str
    description: str
    price: int
    seller_id: int
    is_active: bool


@pytest.mark.asyncio
async def test_create_product_returns_created_product(stub_product_uow_factory):
    # given
    product_input: ProductInput = {
        'name': 'Test Product',
        'description': 'A product for testing',
        'price': 150,
        'seller_id': 7,
        'is_active': True,
    }
    created_product = evolve(
        Product.create(
            name=product_input['name'],
            description=product_input['description'],
            price=product_input['price'],
            seller_id=product_input['seller_id'],
            is_active=product_input['is_active'],
        ),
        id=99,
    )
    uow: StubProductUnitOfWork = stub_product_uow_factory(created_product=created_product)
    use_case = CreateProductUseCase(uow=cast(AbstractUnitOfWork, uow))

    # when
    result = await use_case.create(
        name=product_input['name'],
        description=product_input['description'],
        price=product_input['price'],
        seller_id=product_input['seller_id'],
        is_active=product_input['is_active'],
    )

    # then
    assert result == created_product
    assert uow.products.received_product is not None
    assert uow.products.received_product.id is None
    assert uow.products.received_product.name == product_input['name']


@pytest.mark.asyncio
async def test_create_product_commits_transaction(stub_product_uow_factory):
    # given
    created_product = evolve(
        Product.create(
            name='Another Product',
            description='Another description',
            price=200,
            seller_id=8,
            is_active=False,
        ),
        id=101,
    )
    uow: StubProductUnitOfWork = stub_product_uow_factory(created_product=created_product)
    use_case = CreateProductUseCase(uow=cast(AbstractUnitOfWork, uow))

    # when
    await use_case.create(
        name='Another Product',
        description='Another description',
        price=200,
        seller_id=8,
        is_active=False,
    )

    # then
    assert uow.commit_called
