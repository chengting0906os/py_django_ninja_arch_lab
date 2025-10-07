from enum import StrEnum


class ProductStatus(StrEnum):
    AVAILABLE = 'available'
    RESERVED = 'reserved'
    SOLD = 'sold'
