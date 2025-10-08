"""Integration tests for order state transitions."""

from ninja_extra.testing import TestAsyncClient
import pytest

from test.order.integration.util import (
    given_logged_in_as_buyer,
    given_seller_with_product,
    when_create_order,
)


@pytest.mark.django_db(transaction=True)
class TestOrderStateTransition:
    """Test order state transition rules."""

    async def test_cannot_cancel_paid_order(self, client: TestAsyncClient):
        """Test that paid orders cannot be cancelled."""
        # Given a product and buyer are logged in
        seller_id, product_id = await given_seller_with_product(
            client, 'Test Product', 'Test Description', 1000, True, 'available'
        )

        await given_logged_in_as_buyer(client, 'buyer@test.com', 'P@ssw0rd')

        # And buyer creates an order
        response = await when_create_order(client, product_id)
        assert response.status_code == 201
        order_id = response.json()['id']

        # And buyer pays for the order
        # pyrefly: ignore  # async-error
        response = await client.post(
            f'/order/{order_id}/pay', json={'card_number': '4242424242424242'}
        )
        assert response.status_code == 200

        # When buyer tries to cancel
        # pyrefly: ignore  # async-error
        response = await client.delete(f'/order/{order_id}')

        # Then
        assert response.status_code == 400
        error_data = response.json()
        assert 'Cannot cancel paid order' in str(
            error_data.get('detail') or error_data.get('message', '')
        )

    async def test_cannot_pay_for_cancelled_order(self, client: TestAsyncClient):
        """Test that cancelled orders cannot be paid."""
        # Given a product and buyer are logged in
        seller_id, product_id = await given_seller_with_product(
            client, 'Test Product', 'Test Description', 1000, True, 'available'
        )

        await given_logged_in_as_buyer(client, 'buyer@test.com', 'P@ssw0rd')

        # And buyer creates an order
        response = await when_create_order(client, product_id)
        assert response.status_code == 201
        order_id = response.json()['id']

        # And buyer cancels the order
        # pyrefly: ignore  # async-error
        response = await client.delete(f'/order/{order_id}')
        assert response.status_code == 204

        # When buyer tries to pay
        # pyrefly: ignore  # async-error
        response = await client.post(
            f'/order/{order_id}/pay', json={'card_number': '4242424242424242'}
        )

        # Then
        assert response.status_code == 400
        error_data = response.json()
        assert 'Cannot pay for cancelled order' in str(
            error_data.get('detail') or error_data.get('message', '')
        )

    async def test_cannot_re_cancel_cancelled_order(self, client: TestAsyncClient):
        """Test that already cancelled orders cannot be cancelled again."""
        # Given a product and buyer are logged in
        seller_id, product_id = await given_seller_with_product(
            client, 'Test Product', 'Test Description', 1000, True, 'available'
        )

        await given_logged_in_as_buyer(client, 'buyer@test.com', 'P@ssw0rd')

        # And buyer creates an order
        response = await when_create_order(client, product_id)
        assert response.status_code == 201
        order_id = response.json()['id']

        # And buyer cancels the order
        # pyrefly: ignore  # async-error
        response = await client.delete(f'/order/{order_id}')
        assert response.status_code == 204

        # When buyer tries to cancel again
        # pyrefly: ignore  # async-error
        response = await client.delete(f'/order/{order_id}')

        # Then
        assert response.status_code == 400
        error_data = response.json()
        assert 'Order already cancelled' in str(
            error_data.get('detail') or error_data.get('message', '')
        )

    async def test_valid_transition_from_pending_payment_to_paid(self, client: TestAsyncClient):
        """Test valid state transition from PENDING_PAYMENT to PAID."""
        # Given a product and buyer are logged in
        seller_id, product_id = await given_seller_with_product(
            client, 'Test Product', 'Test Description', 1000, True, 'available'
        )

        await given_logged_in_as_buyer(client, 'buyer@test.com', 'P@ssw0rd')

        # And buyer creates an order
        response = await when_create_order(client, product_id)
        assert response.status_code == 201
        order_id = response.json()['id']

        # When buyer pays for the order
        # pyrefly: ignore  # async-error
        response = await client.post(
            f'/order/{order_id}/pay', json={'card_number': '4242424242424242'}
        )

        # Then
        assert response.status_code == 200

        # Verify order status is paid
        # pyrefly: ignore  # async-error
        response = await client.get(f'/order/{order_id}')
        assert response.status_code == 200
        order = response.json()
        assert order['status'] == 'paid'

    async def test_valid_transition_from_pending_payment_to_cancelled(
        self, client: TestAsyncClient
    ):
        """Test valid state transition from PENDING_PAYMENT to CANCELLED."""
        # Given a product and buyer are logged in
        seller_id, product_id = await given_seller_with_product(
            client, 'Test Product', 'Test Description', 1000, True, 'available'
        )

        await given_logged_in_as_buyer(client, 'buyer@test.com', 'P@ssw0rd')

        # And buyer creates an order
        response = await when_create_order(client, product_id)
        assert response.status_code == 201
        order_id = response.json()['id']

        # When buyer cancels the order
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
