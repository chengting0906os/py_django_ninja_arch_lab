"""Unit tests for DeleteProductUseCase."""

from unittest.mock import AsyncMock, Mock

import pytest

from src.app.use_case.product.delete_product_use_case import DeleteProductUseCase
from src.domain.entity.product_entity import Product
from src.domain.enum.product_status import ProductStatus


def _build_product(product_id: int, name: str, status: ProductStatus) -> Product:
    return Product(
        id=product_id,
        name=name,
        description=f'{name} description',
        price=100,
        seller_id=1,
        is_active=True,
        status=status,
    )


@pytest.mark.asyncio
async def test_delete_product_returns_true_for_available_product():
    """Test deleting an available product returns True."""
    # Given
    product = _build_product(1, 'Available Product', ProductStatus.AVAILABLE)
    mock_repo = Mock()
    mock_repo.get_by_id = AsyncMock(return_value=product)
    mock_repo.delete = AsyncMock(return_value=True)

    # Inject mock repo via constructor
    use_case = DeleteProductUseCase(product_repo=mock_repo)

    # When
    result = await use_case.delete(product_id=1)

    # Then
    assert result is True
    mock_repo.get_by_id.assert_called_once_with(1)
    mock_repo.delete.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_delete_product_returns_false_when_not_found():
    """Test deleting a non-existent product returns False."""
    # Given
    mock_repo = Mock()
    mock_repo.get_by_id = AsyncMock(return_value=None)
    mock_repo.delete = AsyncMock()

    # Inject mock repo via constructor
    use_case = DeleteProductUseCase(product_repo=mock_repo)

    # When
    result = await use_case.delete(product_id=999)

    # Then
    assert result is False
    mock_repo.get_by_id.assert_called_once_with(999)
    mock_repo.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_product_raises_for_reserved_status():
    """Test deleting a reserved product raises ValueError."""
    # Given
    product = _build_product(2, 'Reserved Product', ProductStatus.RESERVED)
    mock_repo = Mock()
    mock_repo.get_by_id = AsyncMock(return_value=product)
    mock_repo.delete = AsyncMock()

    # Inject mock repo via constructor
    use_case = DeleteProductUseCase(product_repo=mock_repo)

    # When / Then
    with pytest.raises(ValueError, match='Cannot delete reserved product'):
        await use_case.delete(product_id=2)

    mock_repo.get_by_id.assert_called_once_with(2)
    mock_repo.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_product_raises_for_sold_status():
    """Test deleting a sold product raises ValueError."""
    # Given
    product = _build_product(3, 'Sold Product', ProductStatus.SOLD)
    mock_repo = Mock()
    mock_repo.get_by_id = AsyncMock(return_value=product)
    mock_repo.delete = AsyncMock()

    # Inject mock repo via constructor
    use_case = DeleteProductUseCase(product_repo=mock_repo)

    # When / Then
    with pytest.raises(ValueError, match='Cannot delete sold product'):
        await use_case.delete(product_id=3)

    mock_repo.get_by_id.assert_called_once_with(3)
    mock_repo.delete.assert_not_called()
