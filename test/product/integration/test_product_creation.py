"""Product creation integration tests using given-when-then pattern."""

from ninja_extra.testing import TestAsyncClient
import pytest

from src.platform.constant.route_constant import PRODUCT_CREATE
from test.product.integration.util import (
    given_logged_in_buyer,
    given_logged_in_seller,
    given_product_payload,
    given_seller_user_exists,
    login_as,
    then_error_message_contains,
)
from test.util_constant import DEFAULT_PASSWORD, TEST_BUYER_EMAIL, TEST_SELLER_EMAIL


@pytest.mark.django_db(transaction=True)
class TestProductCreation:
    @pytest.mark.asyncio
    async def test_create_product_successfully(self, client: TestAsyncClient):
        """Test creating a new product successfully."""
        # Given
        await given_seller_user_exists(client, TEST_SELLER_EMAIL, DEFAULT_PASSWORD)
        product_data = given_product_payload('iPhone 18', 'Latest Apple smartphone', 1500)

        # When - login before creating product
        await login_as(client, TEST_SELLER_EMAIL, DEFAULT_PASSWORD)
        response = await self._when_create_product(client, product_data)

        # Then
        self._then_product_created_successfully(response, product_data)

    @pytest.mark.asyncio
    async def test_create_product_with_negative_price(self, client: TestAsyncClient):
        """Test creating a product with negative price should fail."""
        # Given
        await given_logged_in_seller(client, TEST_SELLER_EMAIL, DEFAULT_PASSWORD)
        product_data = given_product_payload('iPhone 25', 'Apple phone', -500)

        # When
        response = await self._when_create_product(client, product_data)

        # Then
        assert response.status_code == 400
        then_error_message_contains(response, 'Price must be positive')

    @pytest.mark.asyncio
    async def test_create_inactive_product(self, client: TestAsyncClient):
        """Test creating an inactive product."""
        # Given
        await given_logged_in_seller(client, TEST_SELLER_EMAIL, DEFAULT_PASSWORD)
        product_data = given_product_payload(
            'iPad Pro', 'Professional tablet', 2000, is_active=False
        )

        # When
        response = await self._when_create_product(client, product_data)

        # Then
        self._then_product_created_successfully(response, product_data)
        response_json = response.json()
        assert response_json['is_active'] is False

    @pytest.mark.asyncio
    async def test_buyer_cannot_create_product(self, client: TestAsyncClient):
        """Test that buyer users cannot create products."""
        # Given
        await given_logged_in_buyer(client, TEST_BUYER_EMAIL, DEFAULT_PASSWORD)
        product_data = given_product_payload('MacBook', 'Apple laptop', 3000)

        # When
        response = await self._when_create_product(client, product_data)

        # Then
        assert response.status_code == 403
        then_error_message_contains(response, 'Only sellers can perform this action')

    # When helpers
    async def _when_create_product(self, client: TestAsyncClient, product_data: dict):
        """Create product via API using Django session authentication."""
        return await client.post(  # pyrefly: ignore[async-error]
            PRODUCT_CREATE, json=product_data
        )

    # Then helpers
    def _then_product_created_successfully(self, response, product_data: dict):
        """Assert product was created successfully."""
        assert response.status_code == 201, (
            f'Expected status 201, got {response.status_code}: {response.json()}'
        )
        response_json = response.json()
        assert response_json['name'] == product_data['name']
        assert response_json['description'] == product_data['description']
        assert response_json['price'] == product_data['price']
        assert 'id' in response_json
        assert response_json['id'] > 0
        assert 'seller_id' in response_json
        assert response_json['seller_id'] > 0
