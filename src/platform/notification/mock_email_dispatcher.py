from typing import List, Optional

from django.utils import timezone

from src.app.interface.i_email_dispatcher import IEmailDispatcher
from src.platform.logging.loguru_io import Logger


class MockEmailDispatcher(IEmailDispatcher):
    def __init__(self):
        self.sent_emails: List[dict] = []

    @Logger.io
    async def send_email(
        self, to: str, subject: str, body: str, cc: Optional[List[str]] = None
    ) -> bool:
        email_data = {
            'to': to,
            'subject': subject,
            'body': body,
            'cc': cc or [],
            'sent_at': timezone.now(),
        }

        self.sent_emails.append(email_data)

        print('\n' + '=' * 50)
        print('📧 MOCK EMAIL SENT')
        print('=' * 50)
        print(f'To: {to}')
        if cc:
            print(f'CC: {", ".join(cc)}')
        print(f'Subject: {subject}')
        print(f'Time: {email_data["sent_at"].strftime("%Y-%m-%d %H:%M:%S")}')
        print('-' * 50)
        print('Body:')
        print(body)
        print('=' * 50 + '\n')

        return True

    @Logger.io
    async def send_order_confirmation(
        self, buyer_email: str, order_id: int, product_name: str, price: int
    ):
        if not order_id or order_id <= 0:
            raise ValueError(f'Invalid order_id: {order_id}. Order ID must be positive.')
        subject = f'Order Confirmation - Order #{order_id}'
        body = f"""
        Dear Customer,

        Thank you for your order!

        Order Details:
        --------------
        Order ID: #{order_id}
        Product: {product_name}
        Price: ${price:,}
        Status: Pending Payment

        Please complete your payment to process this order.

        Best regards,
        Shopping Platform Team
        """
        await self.send_email(buyer_email, subject, body.strip())

    @Logger.io
    async def send_payment_confirmation(
        self, buyer_email: str, order_id: int, product_name: str, paid_amount: int
    ):
        if not order_id or order_id <= 0:
            raise ValueError(f'Invalid order_id: {order_id}. Order ID must be positive.')
        subject = f'Payment Confirmed - Order #{order_id}'
        body = f"""
        Dear Customer,

        Your payment has been successfully processed!

        Payment Details:
        ----------------
        Order ID: #{order_id}
        Product: {product_name}
        Amount Paid: ${paid_amount:,}
        Status: Paid

        Your order is now being processed.

        Best regards,
        Shopping Platform Team
        """
        await self.send_email(buyer_email, subject, body.strip())

    @Logger.io
    async def send_order_cancellation(self, buyer_email: str, order_id: int, product_name: str):
        if not order_id or order_id <= 0:
            raise ValueError(f'Invalid order_id: {order_id}. Order ID must be positive.')
        subject = f'Order Cancelled - Order #{order_id}'
        body = f"""
        Dear Customer,

        Your order has been cancelled.

        Cancellation Details:
        --------------------
        Order ID: #{order_id}
        Product: {product_name}

        If you have any questions, please contact our support team.

        Best regards,
        Shopping Platform Team
        """
        await self.send_email(buyer_email, subject, body.strip())

    @Logger.io
    async def notify_seller_new_order(
        self, seller_email: str, order_id: int, product_name: str, buyer_name: str, price: int
    ):
        if not order_id or order_id <= 0:
            raise ValueError(f'Invalid order_id: {order_id}. Order ID must be positive.')
        subject = f'New Order Received - Order #{order_id}'
        body = f"""
        Dear Seller,

        You have received a new order!

        Order Details:
        --------------
        Order ID: #{order_id}
        Product: {product_name}
        Buyer: {buyer_name}
        Price: ${price:,}

        The buyer will complete payment soon.

        Best regards,
        Shopping Platform Team
        """
        await self.send_email(seller_email, subject, body.strip())


# Global instance for dependency injection
mock_email_dispatcher = MockEmailDispatcher()


@Logger.io
def get_mock_email_dispatcher() -> MockEmailDispatcher:
    return mock_email_dispatcher
