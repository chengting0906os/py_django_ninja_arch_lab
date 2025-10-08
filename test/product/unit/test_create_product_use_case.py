"""Unit tests for CreateProductUseCase."""

from unittest.mock import AsyncMock, Mock

import pytest

from src.app.use_case.product.create_product_use_case import CreateProductUseCase
from src.domain.entity.product_entity import Product
from src.domain.enum.product_status import ProductStatus


@pytest.mark.asyncio
async def test_create_product_returns_created_product():
    """Test that create product use case returns the created product."""
    # Given
    mock_repo = Mock()
    created_product = Product(
        id=99,
        name='Test Product',
        description='A product for testing',
        price=150,
        seller_id=7,
        is_active=True,
        status=ProductStatus.AVAILABLE,
    )
    mock_repo.create = AsyncMock(return_value=created_product)

    # Inject mock repo via constructor
    use_case = CreateProductUseCase(product_repo=mock_repo)

    # When
    result = await use_case.create(
        name='Test Product',
        description='A product for testing',
        price=150,
        seller_id=7,
        is_active=True,
    )

    # Then
    assert result == created_product
    assert result.id == 99
    assert result.name == 'Test Product'
    mock_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_product_calls_repo_with_correct_entity():
    """Test that create product use case passes correct entity to repo."""
    # Given
    mock_repo = Mock()
    created_product = Product(
        id=101,
        name='Another Product',
        description='Another description',
        price=200,
        seller_id=8,
        is_active=False,
        status=ProductStatus.AVAILABLE,
    )
    mock_repo.create = AsyncMock(return_value=created_product)

    # Inject mock repo via constructor
    use_case = CreateProductUseCase(product_repo=mock_repo)

    # When
    await use_case.create(
        name='Another Product',
        description='Another description',
        price=200,
        seller_id=8,
        is_active=False,
    )

    # Then
    mock_repo.create.assert_called_once()
    call_args = mock_repo.create.call_args[0][0]
    assert isinstance(call_args, Product)
    assert call_args.name == 'Another Product'
    assert call_args.description == 'Another description'
    assert call_args.price == 200
    assert call_args.seller_id == 8
    assert call_args.is_active is False
    assert call_args.id is None  # Should be None before creation
