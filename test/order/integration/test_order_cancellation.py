"""Integration tests for order cancellation."""

import pytest
from ninja_extra.testing import TestAsyncClient

from test.order.integration.util import (
    given_logged_in_as_buyer,
    given_logged_in_as_seller,
    given_orders_exist,
    given_products_exist,
    given_users_exist,
    then_product_status_should_be,
)


@pytest.mark.django_db(transaction=True)
class TestOrderCancellation:
    """Test order cancellation functionality."""

    async def test_successfully_cancel_unpaid_order(self, client: TestAsyncClient):
        """Test successfully cancelling an unpaid order."""
        # Given users exist
        users = await given_users_exist(
            client,
            [
                {
                    'email': 'seller@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Seller',
                    'role': 'seller',
                },
                {
                    'email': 'buyer@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Buyer',
                    'role': 'buyer',
                },
            ],
        )
        seller_id = users['seller@test.com']
        buyer_id = users['buyer@test.com']

        # And product exists
        products = await given_products_exist(
            client, seller_id, [{'name': 'Test Product', 'price': 2000, 'status': 'reserved'}]
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
                    'price': 2000,
                    'status': 'pending_payment',
                    'paid_at': None,
                }
            ],
        )
        order_id = orders[0]

        # When buyer cancels the order
        await given_logged_in_as_buyer(client, 'buyer@test.com', 'P@ssw0rd')
        # pyrefly: ignore  # async-error
        response = await client.delete(f'/order/{order_id}')

        # Then
        assert response.status_code == 204

        # Verify order status is cancelled
        # pyrefly: ignore  # async-error
        response = await client.get(f'/order/{order_id}')
        assert response.status_code == 200
        order = response.json()
        assert order['status'] == 'cancelled'
        assert order['paid_at'] is None

        # Verify product status is available
        await then_product_status_should_be(product_id, 'available')

    async def test_cannot_cancel_paid_order(self, client: TestAsyncClient):
        """Test that cancelling a paid order fails."""
        # Given users and order exist
        users = await given_users_exist(
            client,
            [
                {
                    'email': 'seller@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Seller',
                    'role': 'seller',
                },
                {
                    'email': 'buyer@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Buyer',
                    'role': 'buyer',
                },
            ],
        )
        seller_id = users['seller@test.com']
        buyer_id = users['buyer@test.com']

        products = await given_products_exist(
            client, seller_id, [{'name': 'Test Product', 'price': 3000, 'status': 'sold'}]
        )
        product_id = products[0]

        orders = await given_orders_exist(
            client,
            [
                {
                    'buyer_id': buyer_id,
                    'seller_id': seller_id,
                    'product_id': product_id,
                    'price': 3000,
                    'status': 'paid',
                    'paid_at': 'not_null',
                }
            ],
        )
        order_id = orders[0]

        # When buyer tries to cancel
        await given_logged_in_as_buyer(client, 'buyer@test.com', 'P@ssw0rd')
        # pyrefly: ignore  # async-error
        response = await client.delete(f'/order/{order_id}')

        # Then
        assert response.status_code == 400
        error_data = response.json()
        assert 'Cannot cancel paid order' in str(
            error_data.get('detail') or error_data.get('message', '')
        )

        # Verify order status remains paid
        # pyrefly: ignore  # async-error
        response = await client.get(f'/order/{order_id}')
        assert response.status_code == 200
        order = response.json()
        assert order['status'] == 'paid'

        # Verify product status remains sold
        await then_product_status_should_be(product_id, 'sold')

    async def test_cannot_cancel_already_cancelled_order(self, client: TestAsyncClient):
        """Test that cancelling an already cancelled order fails."""
        # Given users and order exist
        users = await given_users_exist(
            client,
            [
                {
                    'email': 'seller@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Seller',
                    'role': 'seller',
                },
                {
                    'email': 'buyer@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Buyer',
                    'role': 'buyer',
                },
            ],
        )
        seller_id = users['seller@test.com']
        buyer_id = users['buyer@test.com']

        products = await given_products_exist(
            client, seller_id, [{'name': 'Test Product', 'price': 1500, 'status': 'available'}]
        )
        product_id = products[0]

        orders = await given_orders_exist(
            client,
            [
                {
                    'buyer_id': buyer_id,
                    'seller_id': seller_id,
                    'product_id': product_id,
                    'price': 1500,
                    'status': 'cancelled',
                    'paid_at': None,
                }
            ],
        )
        order_id = orders[0]

        # When buyer tries to cancel again
        await given_logged_in_as_buyer(client, 'buyer@test.com', 'P@ssw0rd')
        # pyrefly: ignore  # async-error
        response = await client.delete(f'/order/{order_id}')

        # Then
        assert response.status_code == 400
        error_data = response.json()
        assert 'Order already cancelled' in str(
            error_data.get('detail') or error_data.get('message', '')
        )

    async def test_only_buyer_can_cancel_own_order(self, client: TestAsyncClient):
        """Test that only the buyer can cancel their own order."""
        # Given users and order exist
        users = await given_users_exist(
            client,
            [
                {
                    'email': 'seller@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Seller',
                    'role': 'seller',
                },
                {
                    'email': 'buyer@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Buyer',
                    'role': 'buyer',
                },
                {
                    'email': 'another@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Another Buyer',
                    'role': 'buyer',
                },
            ],
        )
        seller_id = users['seller@test.com']
        buyer_id = users['buyer@test.com']
        _ = users['another@test.com']

        products = await given_products_exist(
            client, seller_id, [{'name': 'Test Product', 'price': 2500, 'status': 'reserved'}]
        )
        product_id = products[0]

        orders = await given_orders_exist(
            client,
            [
                {
                    'buyer_id': buyer_id,
                    'seller_id': seller_id,
                    'product_id': product_id,
                    'price': 2500,
                    'status': 'pending_payment',
                    'paid_at': None,
                }
            ],
        )
        order_id = orders[0]

        # When another user tries to cancel
        await given_logged_in_as_buyer(client, 'another@test.com', 'P@ssw0rd')
        # pyrefly: ignore  # async-error
        response = await client.delete(f'/order/{order_id}')

        # Then
        assert response.status_code == 403
        error_data = response.json()
        assert 'Only the buyer can cancel this order' in str(
            error_data.get('detail') or error_data.get('message', '')
        )

        # Verify order status remains pending_payment
        # pyrefly: ignore  # async-error
        response = await client.get(f'/order/{order_id}')
        assert response.status_code == 200
        order = response.json()
        assert order['status'] == 'pending_payment'

        # Verify product status remains reserved
        await then_product_status_should_be(product_id, 'reserved')

    async def test_seller_cannot_cancel_buyers_order(self, client: TestAsyncClient):
        """Test that seller cannot cancel buyer's order."""
        # Given users and order exist
        users = await given_users_exist(
            client,
            [
                {
                    'email': 'seller@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Seller',
                    'role': 'seller',
                },
                {
                    'email': 'buyer@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Buyer',
                    'role': 'buyer',
                },
            ],
        )
        seller_id = users['seller@test.com']
        buyer_id = users['buyer@test.com']

        products = await given_products_exist(
            client, seller_id, [{'name': 'Test Product', 'price': 4000, 'status': 'reserved'}]
        )
        product_id = products[0]

        orders = await given_orders_exist(
            client,
            [
                {
                    'buyer_id': buyer_id,
                    'seller_id': seller_id,
                    'product_id': product_id,
                    'price': 4000,
                    'status': 'pending_payment',
                    'paid_at': None,
                }
            ],
        )
        order_id = orders[0]

        # When seller tries to cancel
        await given_logged_in_as_seller(client, 'seller@test.com', 'P@ssw0rd')
        # pyrefly: ignore  # async-error
        response = await client.delete(f'/order/{order_id}')

        # Then
        assert response.status_code == 403
        error_data = response.json()
        # Check for either error message (depends on implementation)
        error_msg = str(error_data.get('detail') or error_data.get('message', ''))
        assert (
            'Only buyers can perform this action' in error_msg
            or 'Only the buyer can cancel this order' in error_msg
        )

        # Verify order status remains pending_payment
        # pyrefly: ignore  # async-error
        response = await client.get(f'/order/{order_id}')
        assert response.status_code == 200
        order = response.json()
        assert order['status'] == 'pending_payment'

        # Verify product status remains reserved
        await then_product_status_should_be(product_id, 'reserved')

    async def test_cannot_cancel_non_existent_order(self, client: TestAsyncClient):
        """Test that cancelling a non-existent order fails."""
        # Given users exist
        users = await given_users_exist(
            client,
            [
                {
                    'email': 'seller@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Seller',
                    'role': 'seller',
                },
                {
                    'email': 'buyer@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Buyer',
                    'role': 'buyer',
                },
            ],
        )
        seller_id = users['seller@test.com']
        _ = users['buyer@test.com']

        # And product exists
        products = await given_products_exist(
            client, seller_id, [{'name': 'Test Product', 'price': 1800, 'status': 'available'}]
        )
        product_id = products[0]

        # When buyer tries to cancel non-existent order
        await given_logged_in_as_buyer(client, 'buyer@test.com', 'P@ssw0rd')
        # pyrefly: ignore  # async-error
        response = await client.delete('/order/99999')

        # Then
        assert response.status_code == 404
        error_data = response.json()
        assert 'Order not found' in str(error_data.get('detail') or error_data.get('message', ''))

        # Verify product status remains available
        await then_product_status_should_be(product_id, 'available')
