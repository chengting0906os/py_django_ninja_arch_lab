"""Django ORM representation for products."""

from django.conf import settings
from django.db import models

from src.domain.enum.product_status import ProductStatus


class ProductModel(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.PositiveIntegerField()
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
    )
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=20,
        # pyrefly: ignore  # not-iterable
        choices=[(status.value, status.value) for status in ProductStatus],
        default=ProductStatus.AVAILABLE.value,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'platform'
        db_table = 'product'
        ordering = ['id']
