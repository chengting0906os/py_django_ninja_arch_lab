from typing import Optional

from pydantic import BaseModel


class ProductCreateRequest(BaseModel):
    name: str
    description: str
    price: int
    is_active: bool = True

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'name': 'iPhone 15 Pro',
                'description': 'Latest Apple smartphone with A17 chip',
                'price': 35900,
                'is_active': True,
            }
        }


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: int
    seller_id: int
    is_active: bool
    status: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'id': 1,
                'name': 'iPhone 15 Pro',
                'description': 'Latest Apple smartphone with A17 chip',
                'price': 35900,
                'seller_id': 2,
                'is_active': True,
                'status': 'available',
            }
        }


class ProductUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'name': 'iPhone 15 Pro Max',
                'description': 'Updated description with more details',
                'price': 42900,
                'is_active': True,
            }
        }
