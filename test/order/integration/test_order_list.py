"""Integration tests for order list functionality."""

import pytest

from test.order.integration.util import (
    given_logged_in_as_buyer,
    given_logged_in_as_seller,
    given_orders_exist,
    given_products_exist,
    given_users_exist,
    then_orders_should_include,
    then_response_should_contain_orders,
    then_response_status_code_should_be,
)


@pytest.mark.django_db(transaction=True)
class TestOrderList:
    """Test order list functionality for buyers and sellers."""

    async def test_buyer_lists_their_orders(self, client):
        """Test that a buyer can list all their orders with details."""
        # client provided by fixture

        # Given users exist
        users = await given_users_exist(
            client,
            [
                {
                    'email': 'seller1@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Seller1',
                    'role': 'seller',
                },
                {
                    'email': 'seller2@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Seller2',
                    'role': 'seller',
                },
                {
                    'email': 'buyer1@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Buyer1',
                    'role': 'buyer',
                },
                {
                    'email': 'buyer2@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Buyer2',
                    'role': 'buyer',
                },
                {
                    'email': 'buyer3@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Buyer3',
                    'role': 'buyer',
                },
            ],
        )

        seller1_id = users['seller1@test.com']
        seller2_id = users['seller2@test.com']
        buyer1_id = users['buyer1@test.com']
        buyer2_id = users['buyer2@test.com']

        # And products exist
        products = await given_products_exist(
            client,
            seller1_id,
            [
                {'name': 'Product A', 'price': 1000, 'status': 'sold'},
                {'name': 'Product B', 'price': 2000, 'status': 'sold'},
            ],
        )
        products_seller2 = await given_products_exist(
            client,
            seller2_id,
            [
                {'name': 'Product C', 'price': 3000, 'status': 'sold'},
            ],
        )
        products_available = await given_products_exist(
            client,
            seller1_id,
            [
                {'name': 'Product D', 'price': 4000, 'status': 'available'},
            ],
        )

        product_a_id = products[0]
        product_b_id = products[1]
        product_c_id = products_seller2[0]
        product_d_id = products_available[0]

        # And orders exist
        await given_orders_exist(
            client,
            [
                {
                    'buyer_id': buyer1_id,
                    'seller_id': seller1_id,
                    'product_id': product_a_id,
                    'price': 1000,
                    'status': 'paid',
                    'paid_at': 'not_null',
                },
                {
                    'buyer_id': buyer1_id,
                    'seller_id': seller1_id,
                    'product_id': product_b_id,
                    'price': 2000,
                    'status': 'paid',
                    'paid_at': 'not_null',
                },
                {
                    'buyer_id': buyer1_id,
                    'seller_id': seller2_id,
                    'product_id': product_c_id,
                    'price': 3000,
                    'status': 'pending_payment',
                    'paid_at': None,
                },
                {
                    'buyer_id': buyer2_id,
                    'seller_id': seller1_id,
                    'product_id': product_d_id,
                    'price': 4000,
                    'status': 'cancelled',
                    'paid_at': None,
                },
            ],
        )

        # When buyer requests their orders
        await given_logged_in_as_buyer(client, 'buyer1@test.com', 'P@ssw0rd')
        response = await client.get('/order/my-orders')

        # Then
        await then_response_status_code_should_be(response, 200)
        await then_response_should_contain_orders(response, 3)
        await then_orders_should_include(
            response,
            [
                {
                    'product_name': 'Product A',
                    'price': 1000,
                    'status': 'paid',
                    'seller_name': 'Test Seller1',
                    'paid_at': 'not_null',
                },
                {
                    'product_name': 'Product B',
                    'price': 2000,
                    'status': 'paid',
                    'seller_name': 'Test Seller1',
                    'paid_at': 'not_null',
                },
                {
                    'product_name': 'Product C',
                    'price': 3000,
                    'status': 'pending_payment',
                    'seller_name': 'Test Seller2',
                    'paid_at': None,
                },
            ],
        )

    async def test_seller_lists_orders_for_their_products(self, client):
        """Test that a seller can list all orders for their products."""
        # client provided by fixture

        # Given users exist
        users = await given_users_exist(
            client,
            [
                {
                    'email': 'seller1@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Seller1',
                    'role': 'seller',
                },
                {
                    'email': 'buyer1@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Buyer1',
                    'role': 'buyer',
                },
                {
                    'email': 'buyer2@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Buyer2',
                    'role': 'buyer',
                },
            ],
        )

        seller1_id = users['seller1@test.com']
        buyer1_id = users['buyer1@test.com']
        buyer2_id = users['buyer2@test.com']

        # And products exist
        products = await given_products_exist(
            client,
            seller1_id,
            [
                {'name': 'Product A', 'price': 1000, 'status': 'sold'},
                {'name': 'Product B', 'price': 2000, 'status': 'sold'},
                {'name': 'Product D', 'price': 4000, 'status': 'available'},
            ],
        )

        product_a_id = products[0]
        product_b_id = products[1]
        product_d_id = products[2]

        # And orders exist
        await given_orders_exist(
            client,
            [
                {
                    'buyer_id': buyer1_id,
                    'seller_id': seller1_id,
                    'product_id': product_a_id,
                    'price': 1000,
                    'status': 'paid',
                    'paid_at': 'not_null',
                },
                {
                    'buyer_id': buyer1_id,
                    'seller_id': seller1_id,
                    'product_id': product_b_id,
                    'price': 2000,
                    'status': 'paid',
                    'paid_at': 'not_null',
                },
                {
                    'buyer_id': buyer2_id,
                    'seller_id': seller1_id,
                    'product_id': product_d_id,
                    'price': 4000,
                    'status': 'cancelled',
                    'paid_at': None,
                },
            ],
        )

        # When seller requests their orders
        await given_logged_in_as_seller(client, 'seller1@test.com', 'P@ssw0rd')
        response = await client.get(f'/order/seller/{seller1_id}')

        # Then
        await then_response_status_code_should_be(response, 200)
        await then_response_should_contain_orders(response, 3)
        await then_orders_should_include(
            response,
            [
                {
                    'product_name': 'Product A',
                    'price': 1000,
                    'status': 'paid',
                    'buyer_name': 'Test Buyer1',
                    'paid_at': 'not_null',
                },
                {
                    'product_name': 'Product B',
                    'price': 2000,
                    'status': 'paid',
                    'buyer_name': 'Test Buyer1',
                    'paid_at': 'not_null',
                },
                {
                    'product_name': 'Product D',
                    'price': 4000,
                    'status': 'cancelled',
                    'buyer_name': 'Test Buyer2',
                    'paid_at': None,
                },
            ],
        )

    async def test_buyer_with_no_orders_gets_empty_list(self, client):
        """Test that a buyer with no orders receives an empty list."""
        # client provided by fixture

        # Given a buyer exists with no orders
        users = await given_users_exist(
            client,
            [
                {
                    'email': 'buyer3@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Buyer3',
                    'role': 'buyer',
                },
            ],
        )

        _ = users['buyer3@test.com']

        # When buyer requests their orders
        await given_logged_in_as_buyer(client, 'buyer3@test.com', 'P@ssw0rd')
        response = await client.get('/order/my-orders')

        # Then
        await then_response_status_code_should_be(response, 200)
        await then_response_should_contain_orders(response, 0)

    async def test_filter_orders_by_status_paid_only(self, client):
        """Test filtering buyer orders to show only paid orders."""
        # client provided by fixture

        # Given users and orders exist
        users = await given_users_exist(
            client,
            [
                {
                    'email': 'seller1@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Seller1',
                    'role': 'seller',
                },
                {
                    'email': 'buyer1@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Buyer1',
                    'role': 'buyer',
                },
            ],
        )

        seller1_id = users['seller1@test.com']
        buyer1_id = users['buyer1@test.com']

        products = await given_products_exist(
            client,
            seller1_id,
            [
                {'name': 'Product A', 'price': 1000, 'status': 'sold'},
                {'name': 'Product B', 'price': 2000, 'status': 'sold'},
                {'name': 'Product C', 'price': 3000, 'status': 'sold'},
            ],
        )

        await given_orders_exist(
            client,
            [
                {
                    'buyer_id': buyer1_id,
                    'seller_id': seller1_id,
                    'product_id': products[0],
                    'price': 1000,
                    'status': 'paid',
                    'paid_at': 'not_null',
                },
                {
                    'buyer_id': buyer1_id,
                    'seller_id': seller1_id,
                    'product_id': products[1],
                    'price': 2000,
                    'status': 'paid',
                    'paid_at': 'not_null',
                },
                {
                    'buyer_id': buyer1_id,
                    'seller_id': seller1_id,
                    'product_id': products[2],
                    'price': 3000,
                    'status': 'pending_payment',
                    'paid_at': None,
                },
            ],
        )

        # When buyer requests orders filtered by 'paid' status
        await given_logged_in_as_buyer(client, 'buyer1@test.com', 'P@ssw0rd')
        response = await client.get('/order/my-orders?order_status=paid')

        # Then
        await then_response_status_code_should_be(response, 200)
        await then_response_should_contain_orders(response, 2)

        # All orders should have status 'paid'
        data = response.json()
        for order in data:
            assert order['status'] == 'paid', f"Expected status 'paid', got '{order['status']}'"

    async def test_filter_orders_by_status_pending_payment_only(self, client):
        """Test filtering buyer orders to show only pending payment orders."""
        # client provided by fixture

        # Given users and orders exist
        users = await given_users_exist(
            client,
            [
                {
                    'email': 'seller1@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Seller1',
                    'role': 'seller',
                },
                {
                    'email': 'buyer1@test.com',
                    'password': 'P@ssw0rd',
                    'name': 'Test Buyer1',
                    'role': 'buyer',
                },
            ],
        )

        seller1_id = users['seller1@test.com']
        buyer1_id = users['buyer1@test.com']

        products = await given_products_exist(
            client,
            seller1_id,
            [
                {'name': 'Product A', 'price': 1000, 'status': 'sold'},
                {'name': 'Product B', 'price': 2000, 'status': 'sold'},
                {'name': 'Product C', 'price': 3000, 'status': 'sold'},
            ],
        )

        await given_orders_exist(
            client,
            [
                {
                    'buyer_id': buyer1_id,
                    'seller_id': seller1_id,
                    'product_id': products[0],
                    'price': 1000,
                    'status': 'paid',
                    'paid_at': 'not_null',
                },
                {
                    'buyer_id': buyer1_id,
                    'seller_id': seller1_id,
                    'product_id': products[1],
                    'price': 2000,
                    'status': 'paid',
                    'paid_at': 'not_null',
                },
                {
                    'buyer_id': buyer1_id,
                    'seller_id': seller1_id,
                    'product_id': products[2],
                    'price': 3000,
                    'status': 'pending_payment',
                    'paid_at': None,
                },
            ],
        )

        # When buyer requests orders filtered by 'pending_payment' status
        await given_logged_in_as_buyer(client, 'buyer1@test.com', 'P@ssw0rd')
        response = await client.get('/order/my-orders?order_status=pending_payment')

        # Then
        await then_response_status_code_should_be(response, 200)
        await then_response_should_contain_orders(response, 1)

        # All orders should have status 'pending_payment'
        data = response.json()
        for order in data:
            assert order['status'] == 'pending_payment', (
                f"Expected status 'pending_payment', got '{order['status']}'"
            )
