"""Unit tests for CreateOrderUseCase."""

from unittest.mock import AsyncMock, Mock

import pytest

from src.app.use_case.order.create_order_use_case import CreateOrderUseCase
from src.domain.entity.order_entity import Order
from src.domain.entity.product_entity import Product
from src.domain.entity.user_entity import User
from src.domain.enum.order_status import OrderStatus
from src.domain.enum.product_status import ProductStatus
from src.domain.enum.user_role_enum import UserRole
from src.platform.exception.exceptions import DomainError
from test.util_constant import TEST_BUYER_EMAIL, TEST_PRODUCT_NAME, TEST_SELLER_EMAIL


@pytest.mark.asyncio
async def test_create_order_returns_created_order():
    """Test that create_order returns the created order with correct values."""
    # Mock repositories
    mock_user_repo = Mock()
    mock_product_repo = Mock()
    mock_order_repo = Mock()
    mock_email_dispatcher = Mock()

    # Setup test data
    buyer = User(id=1, email=TEST_BUYER_EMAIL, name='Buyer', role=UserRole.BUYER)
    seller = User(id=2, email=TEST_SELLER_EMAIL, name='Seller', role=UserRole.SELLER)
    product = Product(
        id=10,
        name=TEST_PRODUCT_NAME,
        description='Test',
        price=1000,
        seller_id=seller.id,
        is_active=True,
        status=ProductStatus.AVAILABLE,
    )
    created_order = Order(
        id=100,
        buyer_id=buyer.id,
        seller_id=seller.id,
        product_id=product.id,
        price=product.price,
        status=OrderStatus.PENDING_PAYMENT,
    )

    # Setup mocks
    mock_user_repo.get_by_id = AsyncMock(return_value=buyer)
    mock_product_repo.get_by_id_with_seller = AsyncMock(return_value=(product, seller))
    mock_product_repo.update = AsyncMock(return_value=product)
    mock_order_repo.create = AsyncMock(return_value=created_order)
    mock_email_dispatcher.send_order_confirmation = AsyncMock()
    mock_email_dispatcher.notify_seller_new_order = AsyncMock()

    # Create use case
    use_case = CreateOrderUseCase(
        email_dispatcher=mock_email_dispatcher,
        user_repo=mock_user_repo,
        product_repo=mock_product_repo,
        order_repo=mock_order_repo,
    )

    # Execute
    result = await use_case.create_order(buyer_id=buyer.id, product_id=product.id or 0)

    # Assert
    assert result.id == 100
    assert result.buyer_id == buyer.id
    assert result.seller_id == seller.id
    assert result.product_id == product.id
    assert result.price == 1000
    assert result.status == OrderStatus.PENDING_PAYMENT

    # Verify repo calls
    mock_user_repo.get_by_id.assert_called_once_with(buyer.id)
    mock_product_repo.get_by_id_with_seller.assert_called_once_with(product.id)
    mock_order_repo.create.assert_called_once()
    mock_product_repo.update.assert_called_once()

    # Verify emails sent
    mock_email_dispatcher.send_order_confirmation.assert_called_once()
    mock_email_dispatcher.notify_seller_new_order.assert_called_once()


@pytest.mark.asyncio
async def test_create_order_raises_error_when_buyer_not_found():
    """Test that create_order raises DomainError when buyer is not found."""
    # Mock repositories
    mock_user_repo = Mock()
    mock_product_repo = Mock()
    mock_order_repo = Mock()
    mock_email_dispatcher = Mock()

    # Setup mocks
    mock_user_repo.get_by_id = AsyncMock(return_value=None)

    # Create use case
    use_case = CreateOrderUseCase(
        email_dispatcher=mock_email_dispatcher,
        user_repo=mock_user_repo,
        product_repo=mock_product_repo,
        order_repo=mock_order_repo,
    )

    # Execute and assert
    with pytest.raises(DomainError, match='Buyer not found'):
        await use_case.create_order(buyer_id=999, product_id=10)

    # Verify no order was created
    mock_order_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_order_raises_error_when_product_not_found():
    """Test that create_order raises DomainError when product is not found."""
    # Mock repositories
    mock_user_repo = Mock()
    mock_product_repo = Mock()
    mock_order_repo = Mock()
    mock_email_dispatcher = Mock()

    # Setup test data
    buyer = User(id=1, email='buyer@test.com', name='Buyer', role=UserRole.BUYER)

    # Setup mocks
    mock_user_repo.get_by_id = AsyncMock(return_value=buyer)
    mock_product_repo.get_by_id_with_seller = AsyncMock(return_value=(None, None))

    # Create use case
    use_case = CreateOrderUseCase(
        email_dispatcher=mock_email_dispatcher,
        user_repo=mock_user_repo,
        product_repo=mock_product_repo,
        order_repo=mock_order_repo,
    )

    # Execute and assert
    with pytest.raises(DomainError, match='Product not found'):
        await use_case.create_order(buyer_id=buyer.id, product_id=999)

    # Verify no order was created
    mock_order_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_order_reserves_product():
    """Test that create_order changes product status to RESERVED."""
    # Mock repositories
    mock_user_repo = Mock()
    mock_product_repo = Mock()
    mock_order_repo = Mock()
    mock_email_dispatcher = Mock()

    # Setup test data
    buyer = User(id=1, email=TEST_BUYER_EMAIL, name='Buyer', role=UserRole.BUYER)
    seller = User(id=2, email=TEST_SELLER_EMAIL, name='Seller', role=UserRole.SELLER)
    product = Product(
        id=10,
        name=TEST_PRODUCT_NAME,
        description='Test',
        price=1000,
        seller_id=seller.id,
        is_active=True,
        status=ProductStatus.AVAILABLE,
    )
    created_order = Order(
        id=100,
        buyer_id=buyer.id,
        seller_id=seller.id,
        product_id=product.id,
        price=product.price,
        status=OrderStatus.PENDING_PAYMENT,
    )

    # Setup mocks
    mock_user_repo.get_by_id = AsyncMock(return_value=buyer)
    mock_product_repo.get_by_id_with_seller = AsyncMock(return_value=(product, seller))
    mock_product_repo.update = AsyncMock(return_value=product)
    mock_order_repo.create = AsyncMock(return_value=created_order)
    mock_email_dispatcher.send_order_confirmation = AsyncMock()
    mock_email_dispatcher.notify_seller_new_order = AsyncMock()

    # Create use case
    use_case = CreateOrderUseCase(
        email_dispatcher=mock_email_dispatcher,
        user_repo=mock_user_repo,
        product_repo=mock_product_repo,
        order_repo=mock_order_repo,
    )

    # Execute
    await use_case.create_order(buyer_id=buyer.id, product_id=product.id or 0)

    # Verify product was updated with RESERVED status
    mock_product_repo.update.assert_called_once()
    updated_product = mock_product_repo.update.call_args[0][0]
    assert updated_product.status == ProductStatus.RESERVED
