"""Unit test for MockEmailService."""

from datetime import datetime

import pytest

from src.platform.notification.mock_email_dispatcher import MockEmailDispatcher
from test.util_constant import TEST_BUYER_NAME, TEST_EMAIL, TEST_PRODUCT_NAME


class TestMockEmailDispatcher:
    @pytest.fixture
    def email_service(self):
        return MockEmailDispatcher()

    @pytest.mark.asyncio
    async def test_send_email(self, email_service):
        result = await email_service.send_email(
            to=TEST_EMAIL, subject='Test Subject', body='Test Body'
        )

        assert result is True
        assert len(email_service.sent_emails) == 1

        sent_email = email_service.sent_emails[0]
        assert sent_email['to'] == TEST_EMAIL
        assert sent_email['subject'] == 'Test Subject'
        assert sent_email['body'] == 'Test Body'
        assert sent_email['cc'] == []
        assert isinstance(sent_email['sent_at'], datetime)

    @pytest.mark.asyncio
    async def test_send_email_with_cc(self, email_service):
        cc_list = ['cc1@example.com', 'cc2@example.com']
        result = await email_service.send_email(
            to=TEST_EMAIL, subject='Test Subject', body='Test Body', cc=cc_list
        )

        assert result is True
        sent_email = email_service.sent_emails[0]
        assert sent_email['cc'] == cc_list

    @pytest.mark.asyncio
    async def test_send_order_confirmation(self, email_service):
        await email_service.send_order_confirmation(
            buyer_email='buyer@example.com', order_id=123, product_name='Test Product', price=10000
        )

        assert len(email_service.sent_emails) == 1
        sent_email = email_service.sent_emails[0]

        assert sent_email['to'] == 'buyer@example.com'
        assert 'Order Confirmation - Order #123' in sent_email['subject']
        assert 'Order ID: #123' in sent_email['body']
        assert TEST_PRODUCT_NAME in sent_email['body']
        assert '$10,000' in sent_email['body']
        assert 'Pending Payment' in sent_email['body']

    @pytest.mark.asyncio
    async def test_send_payment_confirmation(self, email_service):
        await email_service.send_payment_confirmation(
            buyer_email='buyer@example.com',
            order_id=456,
            product_name='Another Product',
            paid_amount=25050,
        )

        assert len(email_service.sent_emails) == 1
        sent_email = email_service.sent_emails[0]

        assert sent_email['to'] == 'buyer@example.com'
        assert 'Payment Confirmed - Order #456' in sent_email['subject']
        assert 'Order ID: #456' in sent_email['body']
        assert 'Another Product' in sent_email['body']
        assert '$25,050' in sent_email['body']
        assert 'Status: Paid' in sent_email['body']

    @pytest.mark.asyncio
    async def test_send_order_cancellation(self, email_service):
        await email_service.send_order_cancellation(
            buyer_email='buyer@example.com', order_id=789, product_name='Cancelled Product'
        )

        assert len(email_service.sent_emails) == 1
        sent_email = email_service.sent_emails[0]

        assert sent_email['to'] == 'buyer@example.com'
        assert 'Order Cancelled - Order #789' in sent_email['subject']
        assert 'Order ID: #789' in sent_email['body']
        assert 'Cancelled Product' in sent_email['body']
        assert 'cancelled' in sent_email['body'].lower()

    @pytest.mark.asyncio
    async def test_notify_seller_new_order(self, email_service):
        await email_service.notify_seller_new_order(
            seller_email='seller@example.com',
            order_id=321,
            product_name='Hot Product',
            buyer_name=TEST_BUYER_NAME,
            price=5099,
        )

        assert len(email_service.sent_emails) == 1
        sent_email = email_service.sent_emails[0]

        assert sent_email['to'] == 'seller@example.com'
        assert 'New Order Received - Order #321' in sent_email['subject']
        assert 'Order ID: #321' in sent_email['body']
        assert 'Hot Product' in sent_email['body']
        assert TEST_BUYER_NAME in sent_email['body']
        assert '$5,099' in sent_email['body']

    @pytest.mark.asyncio
    @pytest.mark.parametrize('order_id', [0, -100])
    async def test_invalid_order_id_raises_error(self, email_service, order_id):
        with pytest.raises(ValueError) as exc_info:
            await email_service.send_order_confirmation(
                buyer_email='buyer@example.com',
                order_id=order_id,
                product_name=TEST_PRODUCT_NAME,
                price=10000,
            )
        assert f'Invalid order_id: {order_id}' in str(exc_info.value)
        assert 'Order ID must be positive' in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_all_email_methods_validate_order_id(self, email_service):
        # Test send_order_cancellation
        with pytest.raises(ValueError):
            await email_service.send_order_cancellation(
                buyer_email='buyer@example.com', order_id=0, product_name='Test Product'
            )

        # Test notify_seller_new_order
        with pytest.raises(ValueError):
            await email_service.notify_seller_new_order(
                seller_email='seller@example.com',
                order_id=0,
                product_name=TEST_PRODUCT_NAME,
                buyer_name='Test Buyer',
                price=10000,
            )
