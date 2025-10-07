from typing import cast

import pytest

from src.app.use_case.product.delete_product_use_case import DeleteProductUseCase
from src.domain.entity.product_entity import Product
from src.domain.enum.product_status import ProductStatus
from src.platform.db.unit_of_work import AbstractUnitOfWork
from test.shared.fakes import FakeProductsRepo, StubProductUnitOfWork


def _build_product(product_id: int, name: str, status: ProductStatus) -> Product:
    product = Product.create(
        name=name,
        description=f'{name} description',
        price=100,
        seller_id=1,
        is_active=True,
    )
    product.id = product_id
    product.status = status
    return product


@pytest.mark.asyncio
async def test_delete_product_returns_true_for_available_product():
    # given
    product_id = 1
    product = _build_product(product_id, 'Available Product', ProductStatus.AVAILABLE)
    repo = FakeProductsRepo(products_by_id={product_id: product})
    uow = StubProductUnitOfWork(products_repo=repo)
    use_case = DeleteProductUseCase(uow=cast(AbstractUnitOfWork, uow))

    # when
    result = await use_case.delete(product_id=1)

    # then
    assert result is True
    assert repo.deleted_ids == [1]
    assert uow.commit_called


@pytest.mark.asyncio
async def test_delete_product_returns_false_when_not_found():
    # given
    repo = FakeProductsRepo(products_by_id={})
    uow = StubProductUnitOfWork(products_repo=repo)
    use_case = DeleteProductUseCase(uow=cast(AbstractUnitOfWork, uow))

    # when
    result = await use_case.delete(product_id=999)

    # then
    assert result is False
    assert repo.deleted_ids == []
    assert not uow.commit_called


@pytest.mark.asyncio
async def test_delete_product_raises_for_reserved_status():
    # given
    product_id = 2
    product = _build_product(product_id, 'Reserved Product', ProductStatus.RESERVED)
    repo = FakeProductsRepo(products_by_id={product_id: product})
    uow = StubProductUnitOfWork(products_repo=repo)
    use_case = DeleteProductUseCase(uow=cast(AbstractUnitOfWork, uow))

    # when / then
    with pytest.raises(ValueError, match='Cannot delete reserved product'):
        await use_case.delete(product_id=2)

    assert repo.deleted_ids == []
    assert not uow.commit_called


@pytest.mark.asyncio
async def test_delete_product_raises_for_sold_status():
    # given
    product_id = 3
    product = _build_product(product_id, 'Sold Product', ProductStatus.SOLD)
    repo = FakeProductsRepo(products_by_id={product_id: product})
    uow = StubProductUnitOfWork(products_repo=repo)
    use_case = DeleteProductUseCase(uow=cast(AbstractUnitOfWork, uow))

    # when / then
    with pytest.raises(ValueError, match='Cannot delete sold product'):
        await use_case.delete(product_id=3)

    assert repo.deleted_ids == []
    assert not uow.commit_called
