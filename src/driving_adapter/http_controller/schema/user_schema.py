"""User schemas mirroring the session-auth workflow."""

from pydantic import BaseModel
from pydantic import EmailStr, Field


class ErrorResponse(BaseModel):
    detail: str


class IdOut(BaseModel):
    id: int


class UserIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: str = Field(default='buyer')


class UserLoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UpdatePasswordIn(BaseModel):
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    id: int
    username: str
    name: str
    email: EmailStr
    role: str
    is_superuser: bool
