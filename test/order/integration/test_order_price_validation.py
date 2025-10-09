"""Integration tests for order price validation."""

from asgiref.sync import sync_to_async
from ninja_extra.testing import TestAsyncClient
import pytest

from src.platform.models.product_model import ProductModel
from test.order.integration.util import (
    given_logged_in_as_buyer,
    given_seller_with_product,
    given_users_exist,
    then_product_status_should_be,
    when_create_order,
)
from test.util_constant import (
    DEFAULT_PASSWORD,
    TEST_BUYER_EMAIL,
    TEST_CARD_NUMBER,
    TEST_PRODUCT_DESCRIPTION,
    TEST_PRODUCT_NAME,
    TEST_SELLER_EMAIL,
    TEST_SELLER_NAME,
)


@pytest.mark.django_db(transaction=True)
class TestOrderPriceValidation:
    """Test order price validation rules."""

    async def test_database_prevents_negative_price_product(self, client: TestAsyncClient):
        """Test that database constraint prevents negative price products."""
        # Given users exist
        users = await given_users_exist(
            client,
            [
                {
                    'email': TEST_SELLER_EMAIL,
                    'password': DEFAULT_PASSWORD,
                    'name': TEST_SELLER_NAME,
                    'role': 'seller',
                },
            ],
        )
        seller_id = users[TEST_SELLER_EMAIL]

        # When trying to create product with negative price directly in DB
        # Then it should raise IntegrityError due to CHECK constraint
        from django.db.utils import IntegrityError

        product_model = ProductModel(
            name=TEST_PRODUCT_NAME,
            description=TEST_PRODUCT_DESCRIPTION,
            price=-100,
            seller_id=seller_id,
            is_active=True,
            status='available',
        )

        with pytest.raises(IntegrityError, match='product_price_check'):
            await sync_to_async(product_model.save)()

    async def test_order_price_matches_product_price_at_creation(self, client: TestAsyncClient):
        """Test that order price matches product price at creation time."""
        # Given a product exists
        seller_id, product_id = await given_seller_with_product(
            client, TEST_PRODUCT_NAME, TEST_PRODUCT_DESCRIPTION, 1000, True, 'available'
        )

        # When buyer creates order
        await given_logged_in_as_buyer(client, TEST_BUYER_EMAIL, DEFAULT_PASSWORD)
        response = await when_create_order(client, product_id)

        # Then
        assert response.status_code == 201
        order = response.json()
        assert order['price'] == 1000
        assert order['status'] == 'pending_payment'

    async def test_product_price_changes_do_not_affect_existing_orders(
        self, client: TestAsyncClient
    ):
        """Test that product price changes don't affect existing orders."""
        # Given a product exists and buyer creates order
        seller_id, product_id = await given_seller_with_product(
            client, TEST_PRODUCT_NAME, TEST_PRODUCT_DESCRIPTION, 1000, True, 'available'
        )

        await given_logged_in_as_buyer(client, TEST_BUYER_EMAIL, DEFAULT_PASSWORD)
        response = await when_create_order(client, product_id)
        assert response.status_code == 201
        order = response.json()
        order_id = order['id']

        # When product price is updated
        product_model = await sync_to_async(ProductModel.objects.get)(id=product_id)
        product_model.price = 2000
        await sync_to_async(product_model.save)()

        # Then existing order price should remain 1000
        # pyrefly: ignore  # async-error
        response = await client.get(f'/order/{order_id}')
        assert response.status_code == 200
        order = response.json()
        assert order['price'] == 1000

        # And product status should be reserved
        await then_product_status_should_be(product_id, 'reserved')

    async def test_new_orders_use_updated_product_price(self, client: TestAsyncClient):
        """Test that new orders use updated product price."""
        # Given a product exists and first buyer creates order
        seller_id, product_id = await given_seller_with_product(
            client, TEST_PRODUCT_NAME, TEST_PRODUCT_DESCRIPTION, 1000, True, 'available'
        )

        await given_logged_in_as_buyer(client, TEST_BUYER_EMAIL, DEFAULT_PASSWORD)
        response = await when_create_order(client, product_id)
        assert response.status_code == 201
        order1_id = response.json()['id']

        # And product price is updated
        product_model = await sync_to_async(ProductModel.objects.get)(id=product_id)
        product_model.price = 2000
        await sync_to_async(product_model.save)()

        # And buyer cancels the order to release the product
        # pyrefly: ignore  # async-error
        response = await client.delete(f'/order/{order1_id}')
        assert response.status_code == 204

        # When another buyer creates order
        users = await given_users_exist(
            client,
            [
                {
                    'email': 'buyer2@test.com',
                    'password': DEFAULT_PASSWORD,
                    'name': 'Buyer 2',
                    'role': 'buyer',
                }
            ],
        )
        _ = users['buyer2@test.com']
        await given_logged_in_as_buyer(client, 'buyer2@test.com', DEFAULT_PASSWORD)
        response = await when_create_order(client, product_id)

        # Then new order should have price 2000
        assert response.status_code == 201
        order2 = response.json()
        assert order2['price'] == 2000

    async def test_paid_order_price_remains_unchanged_after_product_price_update(
        self, client: TestAsyncClient
    ):
        """Test that paid order price remains unchanged after product price update."""
        # Given a product exists and buyer creates and pays for order
        seller_id, product_id = await given_seller_with_product(
            client, TEST_PRODUCT_NAME, TEST_PRODUCT_DESCRIPTION, 1500, True, 'available'
        )

        await given_logged_in_as_buyer(client, TEST_BUYER_EMAIL, DEFAULT_PASSWORD)
        response = await when_create_order(client, product_id)
        assert response.status_code == 201
        order = response.json()
        order_id = order['id']

        # And buyer pays for order
        # pyrefly: ignore  # async-error
        response = await client.post(
            f'/order/{order_id}/pay', json={'card_number': TEST_CARD_NUMBER}
        )
        assert response.status_code == 200

        # When product price is updated
        product_model = await sync_to_async(ProductModel.objects.get)(id=product_id)
        product_model.price = 3000
        await sync_to_async(product_model.save)()

        # Then paid order price should remain 1500
        # pyrefly: ignore  # async-error
        response = await client.get(f'/order/{order_id}')
        assert response.status_code == 200
        order = response.json()
        assert order['price'] == 1500
        assert order['status'] == 'paid'
