"""Product list integration tests using given-when-then pattern."""

from ninja_extra.testing import TestAsyncClient
import pytest

from src.platform.constant.route_constant import PRODUCT_CREATE, PRODUCT_LIST
from test.product.integration.util import given_logged_in_seller
from test.util_constant import DEFAULT_PASSWORD, TEST_SELLER_EMAIL


@pytest.mark.django_db(transaction=True)
class TestProductList:
    @pytest.mark.asyncio
    async def test_seller_sees_all_their_products(self, client: TestAsyncClient):
        """Test that sellers can see all their products regardless of status."""
        # Given
        seller_id = await given_logged_in_seller(client, TEST_SELLER_EMAIL, DEFAULT_PASSWORD)
        await self._given_seller_has_products(
            client,
            [
                ('Product A', 'Active available', 1000, True, 'available'),
                ('Product B', 'Inactive available', 2000, False, 'available'),
                ('Product C', 'Active reserved', 3000, True, 'reserved'),
                ('Product D', 'Active sold', 4000, True, 'sold'),
                ('Product E', 'Active available', 1000, True, 'available'),
            ],
        )

        # When
        response = await self._when_request_seller_products(client, seller_id)

        # Then
        assert response.status_code == 200
        products = response.json()
        assert len(products) == 5, f'Expected 5 products, got {len(products)}'
        # Verify all statuses are present
        statuses = {p['status'] for p in products}
        assert 'available' in statuses
        assert 'reserved' in statuses
        assert 'sold' in statuses

    @pytest.mark.asyncio
    async def test_buyer_sees_only_active_and_available_products(self, client: TestAsyncClient):
        """Test that buyers only see active and available products."""
        # Given
        await given_logged_in_seller(client, TEST_SELLER_EMAIL, DEFAULT_PASSWORD)
        await self._given_seller_has_products(
            client,
            [
                ('Product A', 'Active available', 1000, True, 'available'),
                ('Product B', 'Inactive available', 2000, False, 'available'),
                ('Product C', 'Active reserved', 3000, True, 'reserved'),
                ('Product D', 'Active sold', 4000, True, 'sold'),
                ('Product E', 'Active available', 1000, True, 'available'),
            ],
        )

        # When
        response = await self._when_request_available_products(client)

        # Then
        assert response.status_code == 200
        products = response.json()
        assert len(products) == 2, f'Expected 2 products, got {len(products)}'
        # Verify only active and available products
        for product in products:
            assert product['is_active'] is True
            assert product['status'] == 'available'
        # Verify specific products
        names = {p['name'] for p in products}
        assert names == {'Product A', 'Product E'}

    @pytest.mark.asyncio
    async def test_empty_product_list_for_buyer(self, client: TestAsyncClient):
        """Test that buyer sees empty list when no available products exist."""
        # Given
        await given_logged_in_seller(client, TEST_SELLER_EMAIL, DEFAULT_PASSWORD)
        await self._given_seller_has_products(
            client,
            [
                ('Product C', 'Active reserved', 3000, True, 'reserved'),
                ('Product D', 'Active sold', 4000, True, 'sold'),
            ],
        )

        # When
        response = await self._when_request_available_products(client)

        # Then
        assert response.status_code == 200
        products = response.json()
        assert len(products) == 0, f'Expected 0 products, got {len(products)}'

    # Given helpers
    async def _given_seller_has_products(
        self, client: TestAsyncClient, products: list[tuple]
    ) -> None:
        """Create products for the logged-in seller."""
        for name, description, price, is_active, status in products:
            product_data = {
                'name': name,
                'description': description,
                'price': price,
                'is_active': is_active,
            }
            response = await client.post(  # pyrefly: ignore[async-error]
                PRODUCT_CREATE, json=product_data
            )
            assert response.status_code == 201, f'Failed to create product: {response.json()}'

            # Update status if not available
            if status != 'available':
                from asgiref.sync import sync_to_async
                from src.driven_adapter.model.product_model import ProductModel

                product_id = response.json()['id']
                product = await sync_to_async(ProductModel.objects.get)(id=product_id)
                product.status = status
                await sync_to_async(product.save)()

    # When helpers
    async def _when_request_seller_products(self, client: TestAsyncClient, seller_id: int):
        """Request products filtered by seller_id."""
        return await client.get(  # pyrefly: ignore[async-error]
            f'{PRODUCT_LIST}?seller_id={seller_id}'
        )

    async def _when_request_available_products(self, client: TestAsyncClient):
        """Request available products (no filter)."""
        return await client.get(PRODUCT_LIST)  # pyrefly: ignore[async-error]
