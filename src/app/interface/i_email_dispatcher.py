"""Email dispatcher abstraction for application layer."""

from abc import ABC, abstractmethod
from typing import List, Optional


class IEmailDispatcher(ABC):
    @abstractmethod
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
    ) -> bool:
        """Send a generic email message."""

    @abstractmethod
    async def send_order_confirmation(
        self,
        buyer_email: str,
        order_id: int,
        product_name: str,
        price: int,
    ) -> None:
        """Notify buyer that the order was created."""

    @abstractmethod
    async def send_payment_confirmation(
        self,
        buyer_email: str,
        order_id: int,
        product_name: str,
        paid_amount: int,
    ) -> None:
        """Notify buyer that the payment was confirmed."""

    @abstractmethod
    async def send_order_cancellation(
        self,
        buyer_email: str,
        order_id: int,
        product_name: str,
    ) -> None:
        """Notify buyer that the order was cancelled."""

    @abstractmethod
    async def notify_seller_new_order(
        self,
        seller_email: str,
        order_id: int,
        product_name: str,
        buyer_name: str,
        price: int,
    ) -> None:
        """Notify seller about a newly created order."""
