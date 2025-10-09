"""Product deletion integration tests using given-when-then pattern."""

from ninja_extra.testing import TestAsyncClient
import pytest

from src.platform.constant.route_constant import PRODUCT_DELETE, PRODUCT_GET
from test.product.integration.util import (
    given_logged_in_seller,
    given_product_exists,
    then_error_message_contains,
)
from test.util_constant import DEFAULT_PASSWORD, SELLER1_EMAIL, SELLER2_EMAIL, TEST_SELLER_EMAIL


@pytest.mark.django_db(transaction=True)
class TestProductDelete:
    @pytest.mark.asyncio
    async def test_delete_available_product(self, client: TestAsyncClient):
        """Test deleting an available product successfully."""
        # Given
        await given_logged_in_seller(client, TEST_SELLER_EMAIL, DEFAULT_PASSWORD)
        product_id = await given_product_exists(client, 'Test Item', 'Item to delete', 1000, True)

        # When
        response = await self._when_delete_product(client, product_id)

        # Then
        assert response.status_code == 204
        await self._then_product_should_not_exist(client, product_id)

    @pytest.mark.asyncio
    async def test_cannot_delete_reserved_product(self, client: TestAsyncClient):
        """Test that reserved products cannot be deleted."""
        # Given
        await given_logged_in_seller(client, TEST_SELLER_EMAIL, DEFAULT_PASSWORD)
        product_id = await self._given_reserved_product_exists(
            client, 'Test Item', 'Reserved item', 1000
        )

        # When
        response = await self._when_delete_product(client, product_id)

        # Then
        assert response.status_code == 400
        then_error_message_contains(response, 'Cannot delete reserved product')

    @pytest.mark.asyncio
    async def test_cannot_delete_sold_product(self, client: TestAsyncClient):
        """Test that sold products cannot be deleted."""
        # Given
        await given_logged_in_seller(client, TEST_SELLER_EMAIL, DEFAULT_PASSWORD)
        product_id = await self._given_sold_product_exists(client, 'Test Item', 'Sold item', 1000)

        # When
        response = await self._when_delete_product(client, product_id)

        # Then
        assert response.status_code == 400
        then_error_message_contains(response, 'Cannot delete sold product')

    @pytest.mark.asyncio
    async def test_cannot_delete_other_sellers_product(self, client: TestAsyncClient):
        """Test that sellers cannot delete other sellers' products."""
        # Given
        await given_logged_in_seller(client, SELLER1_EMAIL, DEFAULT_PASSWORD)
        product_id = await given_product_exists(client, 'Test Item', 'Item to delete', 1000, True)

        # Login as different seller
        await given_logged_in_seller(client, SELLER2_EMAIL, DEFAULT_PASSWORD)

        # When
        response = await self._when_delete_product(client, product_id)

        # Then
        assert response.status_code == 403
        then_error_message_contains(response, 'You can only delete your own products')

    # Given helpers
    async def _given_reserved_product_exists(
        self, client: TestAsyncClient, name: str, description: str, price: int
    ) -> int:
        """Create a reserved product and return its ID."""
        from asgiref.sync import sync_to_async
        from src.platform.models.product_model import ProductModel

        product_id = await given_product_exists(client, name, description, price, True)

        # Update status to reserved
        product = await sync_to_async(ProductModel.objects.get)(id=product_id)
        product.status = 'reserved'
        await sync_to_async(product.save)()

        return product_id

    async def _given_sold_product_exists(
        self, client: TestAsyncClient, name: str, description: str, price: int
    ) -> int:
        """Create a sold product and return its ID."""
        from asgiref.sync import sync_to_async
        from src.platform.models.product_model import ProductModel

        product_id = await given_product_exists(client, name, description, price, True)

        # Update status to sold
        product = await sync_to_async(ProductModel.objects.get)(id=product_id)
        product.status = 'sold'
        await sync_to_async(product.save)()

        return product_id

    # When helpers
    async def _when_delete_product(self, client: TestAsyncClient, product_id: int):
        """Delete product via API using Django session authentication."""
        url = PRODUCT_DELETE.format(product_id=product_id)
        return await client.delete(url)  # pyrefly: ignore[async-error]

    # Then helpers
    async def _then_product_should_not_exist(self, client: TestAsyncClient, product_id: int):
        """Assert that product no longer exists."""
        url = PRODUCT_GET.format(product_id=product_id)
        response = await client.get(url)  # pyrefly: ignore[async-error]
        assert response.status_code == 404, (
            f'Product should not exist, but got status {response.status_code}'
        )
