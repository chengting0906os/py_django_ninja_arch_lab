"""Integration tests for order payment and cancellation."""

from ninja_extra.testing import TestAsyncClient
import pytest

from test.order.integration.util import (
    given_logged_in_as_buyer,
    given_orders_exist,
    given_products_exist,
    given_users_exist,
    then_product_status_should_be,
)
from test.util_constant import (
    DEFAULT_PASSWORD,
    TEST_BUYER_EMAIL,
    TEST_CARD_NUMBER,
    TEST_SELLER_EMAIL,
)


@pytest.mark.django_db(transaction=True)
class TestOrderPayment:
    """Test order payment functionality."""

    async def test_successfully_pay_for_order(self, client: TestAsyncClient):
        """Test successfully paying for a pending payment order."""
        # Given users exist
        users = await given_users_exist(
            client,
            [
                {'email': TEST_SELLER_EMAIL, 'password': DEFAULT_PASSWORD, 'role': 'seller'},
                {'email': TEST_BUYER_EMAIL, 'password': DEFAULT_PASSWORD, 'role': 'buyer'},
            ],
        )
        seller_id = users[TEST_SELLER_EMAIL]
        buyer_id = users[TEST_BUYER_EMAIL]

        # And product exists
        products = await given_products_exist(
            client, seller_id, [{'name': 'Product A', 'price': 1000, 'status': 'reserved'}]
        )
        product_id = products[0]

        # And order exists
        orders = await given_orders_exist(
            client,
            [
                {
                    'buyer_id': buyer_id,
                    'seller_id': seller_id,
                    'product_id': product_id,
                    'price': 1000,
                    'status': 'pending_payment',
                    'paid_at': None,
                }
            ],
        )
        order_id = orders[0]

        # When buyer pays for the order
        await given_logged_in_as_buyer(client, TEST_BUYER_EMAIL, DEFAULT_PASSWORD)
        # pyrefly: ignore  # async-error
        response = await client.post(
            f'/order/{order_id}/pay',
            json={'card_number': TEST_CARD_NUMBER},
        )

        # Then
        assert response.status_code == 200, (
            f'Expected 200, got {response.status_code}: {response.json()}'
        )

        payment_result = response.json()
        assert payment_result['status'] == 'paid'
        assert payment_result['order_id'] == order_id
        assert 'payment_id' in payment_result
        assert payment_result['payment_id'].startswith('PAY_MOCK_')
        assert payment_result['paid_at'] is not None

        # Verify order status is paid
        # pyrefly: ignore  # async-error
        response = await client.get(f'/order/{order_id}')
        assert response.status_code == 200
        order = response.json()
        assert order['status'] == 'paid'
        assert order['paid_at'] is not None
        assert order['created_at'] is not None

        # Verify product status is sold
        await then_product_status_should_be(product_id, 'sold')

    async def test_cannot_pay_for_already_paid_order(self, client: TestAsyncClient):
        """Test that paying for an already paid order fails."""
        # Given users and order exist
        users = await given_users_exist(
            client,
            [
                {'email': TEST_SELLER_EMAIL, 'password': DEFAULT_PASSWORD, 'role': 'seller'},
                {'email': TEST_BUYER_EMAIL, 'password': DEFAULT_PASSWORD, 'role': 'buyer'},
            ],
        )
        seller_id = users[TEST_SELLER_EMAIL]
        buyer_id = users[TEST_BUYER_EMAIL]

        products = await given_products_exist(
            client, seller_id, [{'name': 'Product A', 'price': 1000, 'status': 'sold'}]
        )
        product_id = products[0]

        orders = await given_orders_exist(
            client,
            [
                {
                    'buyer_id': buyer_id,
                    'seller_id': seller_id,
                    'product_id': product_id,
                    'price': 1000,
                    'status': 'paid',
                    'paid_at': 'not_null',
                }
            ],
        )
        order_id = orders[0]

        # When buyer tries to pay again
        await given_logged_in_as_buyer(client, TEST_BUYER_EMAIL, DEFAULT_PASSWORD)
        # pyrefly: ignore  # async-error
        response = await client.post(
            f'/order/{order_id}/pay',
            json={'card_number': TEST_CARD_NUMBER},
        )

        # Then
        assert response.status_code == 400
        error_data = response.json()
        assert 'Order already paid' in str(
            error_data.get('detail') or error_data.get('message', '')
        )

    async def test_cannot_pay_for_cancelled_order(self, client: TestAsyncClient):
        """Test that paying for a cancelled order fails."""
        # Given users and order exist
        users = await given_users_exist(
            client,
            [
                {'email': TEST_SELLER_EMAIL, 'password': DEFAULT_PASSWORD, 'role': 'seller'},
                {'email': TEST_BUYER_EMAIL, 'password': DEFAULT_PASSWORD, 'role': 'buyer'},
            ],
        )
        seller_id = users[TEST_SELLER_EMAIL]
        buyer_id = users[TEST_BUYER_EMAIL]

        products = await given_products_exist(
            client, seller_id, [{'name': 'Product A', 'price': 1000, 'status': 'available'}]
        )
        product_id = products[0]

        orders = await given_orders_exist(
            client,
            [
                {
                    'buyer_id': buyer_id,
                    'seller_id': seller_id,
                    'product_id': product_id,
                    'price': 1000,
                    'status': 'cancelled',
                    'paid_at': None,
                }
            ],
        )
        order_id = orders[0]

        # When buyer tries to pay
        await given_logged_in_as_buyer(client, TEST_BUYER_EMAIL, DEFAULT_PASSWORD)
        # pyrefly: ignore  # async-error
        response = await client.post(
            f'/order/{order_id}/pay',
            json={'card_number': TEST_CARD_NUMBER},
        )

        # Then
        assert response.status_code == 400
        error_data = response.json()
        assert 'Cannot pay for cancelled order' in str(
            error_data.get('detail') or error_data.get('message', '')
        )

    async def test_only_buyer_can_pay_for_order(self, client: TestAsyncClient):
        """Test that only the buyer can pay for their order."""
        # Given users and order exist
        users = await given_users_exist(
            client,
            [
                {'email': TEST_SELLER_EMAIL, 'password': DEFAULT_PASSWORD, 'role': 'seller'},
                {'email': TEST_BUYER_EMAIL, 'password': DEFAULT_PASSWORD, 'role': 'buyer'},
                {'email': 'other@test.com', 'password': DEFAULT_PASSWORD, 'role': 'buyer'},
            ],
        )
        seller_id = users[TEST_SELLER_EMAIL]
        buyer_id = users[TEST_BUYER_EMAIL]
        _ = users['other@test.com']

        products = await given_products_exist(
            client, seller_id, [{'name': 'Product A', 'price': 1000, 'status': 'reserved'}]
        )
        product_id = products[0]

        orders = await given_orders_exist(
            client,
            [
                {
                    'buyer_id': buyer_id,
                    'seller_id': seller_id,
                    'product_id': product_id,
                    'price': 1000,
                    'status': 'pending_payment',
                    'paid_at': None,
                }
            ],
        )
        order_id = orders[0]

        # When another user tries to pay
        await given_logged_in_as_buyer(client, 'other@test.com', DEFAULT_PASSWORD)
        # pyrefly: ignore  # async-error
        response = await client.post(
            f'/order/{order_id}/pay',
            json={'card_number': TEST_CARD_NUMBER},
        )

        # Then
        assert response.status_code == 403
        error_data = response.json()
        assert 'Only the buyer can pay for this order' in str(
            error_data.get('detail') or error_data.get('message', '')
        )
