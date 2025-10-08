"""Product update integration tests using given-when-then pattern."""

from ninja_extra.testing import TestAsyncClient
import pytest

from src.platform.constant.route_constant import PRODUCT_UPDATE
from test.product.integration.util import (
    given_logged_in_seller,
    given_product_exists,
    then_error_message_contains,
)


@pytest.mark.django_db(transaction=True)
class TestProductUpdate:
    @pytest.mark.asyncio
    async def test_deactivate_product(self, client: TestAsyncClient):
        """Test deactivating a product."""
        # Given
        await given_logged_in_seller(client, 'seller@test.com', 'P@ssw0rd')
        product_id = await given_product_exists(
            client, 'iPhone 18', 'Latest Apple smartphone', 1500, True
        )

        # When
        update_data = {
            'name': 'iPhone 18',
            'description': 'Latest Apple smartphone',
            'price': 1500,
            'is_active': False,
        }
        response = await self._when_update_product(client, product_id, update_data)

        # Then
        assert response.status_code == 200
        product = response.json()
        assert product['name'] == 'iPhone 18'
        assert product['description'] == 'Latest Apple smartphone'
        assert product['price'] == 1500
        assert product['is_active'] is False
        assert product['status'] == 'available'

    @pytest.mark.asyncio
    async def test_update_product_price(self, client: TestAsyncClient):
        """Test updating product price."""
        # Given
        await given_logged_in_seller(client, 'seller@test.com', 'P@ssw0rd')
        product_id = await given_product_exists(
            client, 'iPhone 18', 'Latest Apple smartphone', 1500, True
        )

        # When
        update_data = {
            'name': 'iPhone 18',
            'description': 'Latest Apple smartphone',
            'price': 1299,
            'is_active': True,
        }
        response = await self._when_update_product(client, product_id, update_data)

        # Then
        assert response.status_code == 200
        product = response.json()
        assert product['price'] == 1299
        assert product['name'] == 'iPhone 18'
        assert product['is_active'] is True

    @pytest.mark.asyncio
    async def test_update_product_with_negative_price_fails(self, client: TestAsyncClient):
        """Test updating product with negative price should fail."""
        # Given
        await given_logged_in_seller(client, 'seller@test.com', 'P@ssw0rd')
        product_id = await given_product_exists(
            client, 'iPhone 18', 'Latest Apple smartphone', 1500, True
        )

        # When
        update_data = {
            'name': 'iPhone 18',
            'description': 'Latest Apple smartphone',
            'price': -100,
            'is_active': True,
        }
        response = await self._when_update_product(client, product_id, update_data)

        # Then
        assert response.status_code == 400
        then_error_message_contains(response, 'Price must be positive')

    @pytest.mark.asyncio
    async def test_update_other_sellers_product_fails(self, client: TestAsyncClient):
        """Test that sellers cannot update other sellers' products."""
        # Given
        await given_logged_in_seller(client, 'seller1@test.com', 'P@ssw0rd')
        product_id = await given_product_exists(
            client, 'iPhone 18', 'Latest Apple smartphone', 1500, True
        )

        # Login as different seller
        await given_logged_in_seller(client, 'seller2@test.com', 'P@ssw0rd')

        # When
        update_data = {
            'name': 'iPhone 18',
            'description': 'Updated by wrong seller',
            'price': 1299,
            'is_active': True,
        }
        response = await self._when_update_product(client, product_id, update_data)

        # Then
        assert response.status_code == 403
        then_error_message_contains(response, 'You can only update your own products')

    # When helpers
    async def _when_update_product(
        self, client: TestAsyncClient, product_id: int, update_data: dict
    ):
        """Update product via API using Django session authentication."""
        url = PRODUCT_UPDATE.format(product_id=product_id)
        return await client.patch(url, json=update_data)  # pyrefly: ignore[async-error]
