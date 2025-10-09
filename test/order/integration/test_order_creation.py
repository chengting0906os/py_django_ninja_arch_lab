"""Order creation integration tests using given-when-then pattern."""

from ninja_extra.testing import TestAsyncClient
import pytest

from test.order.integration.util import (
    given_logged_in_as_buyer,
    given_logged_in_as_seller,
    given_seller_with_product,
    then_error_message_contains,
    then_order_created_successfully,
    then_product_status_should_be,
    when_create_order,
)
from test.util_constant import DEFAULT_PASSWORD, TEST_BUYER_EMAIL, TEST_PRODUCT_NAME


@pytest.mark.django_db(transaction=True)
class TestOrderCreation:
    @pytest.mark.asyncio
    async def test_successfully_create_order_for_available_product(self, client: TestAsyncClient):
        """Test creating order for available product successfully."""
        # Given
        seller_id, product_id = await given_seller_with_product(
            client, TEST_PRODUCT_NAME, 'For order test', 1000, True, 'available'
        )
        await given_logged_in_as_buyer(client, TEST_BUYER_EMAIL, DEFAULT_PASSWORD)

        # When
        response = await when_create_order(client, product_id)

        # Then
        then_order_created_successfully(response, 1000)
        await then_product_status_should_be(product_id, 'reserved')

    @pytest.mark.asyncio
    async def test_cannot_create_order_for_reserved_product(self, client: TestAsyncClient):
        """Test that creating order for reserved product should fail."""
        # Given
        seller_id, product_id = await given_seller_with_product(
            client, TEST_PRODUCT_NAME, 'Already reserved', 1000, True, 'reserved'
        )
        await given_logged_in_as_buyer(client, TEST_BUYER_EMAIL, DEFAULT_PASSWORD)

        # When
        response = await when_create_order(client, product_id)

        # Then
        assert response.status_code == 400
        then_error_message_contains(response, 'Product not available')

    @pytest.mark.asyncio
    async def test_cannot_create_order_for_inactive_product(self, client: TestAsyncClient):
        """Test that creating order for inactive product should fail."""
        # Given
        seller_id, product_id = await given_seller_with_product(
            client, TEST_PRODUCT_NAME, 'Inactive product', 1000, False, 'available'
        )
        await given_logged_in_as_buyer(client, TEST_BUYER_EMAIL, DEFAULT_PASSWORD)

        # When
        response = await when_create_order(client, product_id)

        # Then
        assert response.status_code == 400
        then_error_message_contains(response, 'Product not active')

    @pytest.mark.asyncio
    async def test_seller_cannot_create_order(self, client: TestAsyncClient):
        """Test that sellers cannot create orders."""
        # Given
        seller_id, product_id = await given_seller_with_product(
            client, TEST_PRODUCT_NAME, 'For order test', 1000, True, 'available'
        )
        # Login as the seller (who created the product)
        # Email is 'seller_test_product@test.com' (spaces converted to underscores)
        await given_logged_in_as_seller(client, 'seller_test_product@test.com', DEFAULT_PASSWORD)

        # When
        response = await when_create_order(client, product_id)

        # Then
        assert response.status_code == 403
        then_error_message_contains(response, 'Only buyers can perform this action')
