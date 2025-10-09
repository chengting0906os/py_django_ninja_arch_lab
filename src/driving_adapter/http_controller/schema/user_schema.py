"""User schemas mirroring the session-auth workflow."""

from pydantic import BaseModel, EmailStr, Field


class ErrorResponse(BaseModel):
    detail: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'detail': 'Error message description',
            }
        }


class IdOut(BaseModel):
    id: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'id': 1,
            }
        }


class UserIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = Field(default='buyer')

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'email': 'b@t.com',
                'password': 'P@ssw0rd',
                'role': 'buyer',
            }
        }


class UserLoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'email': 'user@example.com',
                'password': 'P@ssw0rd',
            }
        }


class UpdatePasswordIn(BaseModel):
    password: str = Field(min_length=8)

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'password': 'NewP@ssw0rd123',
            }
        }


class UserOut(BaseModel):
    id: int
    username: str
    name: str
    email: EmailStr
    role: str
    is_superuser: bool

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'id': 1,
                'username': 'user@example.com',
                'name': 'user@example.com',
                'email': 'user@example.com',
                'role': 'buyer',
                'is_superuser': False,
            }
        }
