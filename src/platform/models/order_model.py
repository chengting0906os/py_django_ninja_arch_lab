"""Order database models."""

from django.conf import settings
from django.db import models

from src.domain.enum.order_status import OrderStatus


class OrderModel(models.Model):
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='buyer_orders',
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller_orders',
    )
    product = models.ForeignKey(
        'models.ProductModel',
        on_delete=models.CASCADE,
        related_name='orders',
    )
    price = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        # pyrefly: ignore  # not-iterable
        choices=[(status.value, status.value) for status in OrderStatus],
        default=OrderStatus.PENDING_PAYMENT.value,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'models'
        db_table = 'order'
        ordering = ['id']
