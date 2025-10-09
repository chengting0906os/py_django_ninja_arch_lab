from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OrderCreateRequest(BaseModel):
    product_id: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'product_id': 1,
            }
        }


class OrderResponse(BaseModel):
    id: int
    buyer_id: int
    seller_id: int
    product_id: int
    price: int
    status: str
    created_at: datetime
    paid_at: Optional[datetime]

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'id': 1,
                'buyer_id': 3,
                'seller_id': 2,
                'product_id': 1,
                'price': 35900,
                'status': 'pending_payment',
                'created_at': '2025-10-09T12:00:00',
                'paid_at': None,
            }
        }


class OrderStatusUpdateRequest(BaseModel):
    status: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'status': 'shipped',
            }
        }


class PaymentRequest(BaseModel):
    card_number: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'card_number': '4111111111111111',
            }
        }


class PaymentResponse(BaseModel):
    order_id: int
    payment_id: str
    status: str
    paid_at: Optional[str]

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'order_id': 1,
                'payment_id': 'pay_1234567890',
                'status': 'paid',
                'paid_at': '2025-10-09T12:30:00',
            }
        }
