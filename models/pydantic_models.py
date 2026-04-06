import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from constants import Roles


class TestUser(BaseModel):
    email: str
    fullName: str
    password: str
    passwordRepeat: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Пароли должны совпадать")
    roles: list[Roles] = [Roles.USER]
    verified: Optional[bool] = None
    banned: Optional[bool] = None

    @field_validator('passwordRepeat')
    def check_password_repeat(cls, value: str, info) -> str:
        if 'password' in info.data and value != info.data['password']:
            raise ValueError('Пароли не совпадают')
        return value


class RegisterUserResponse(BaseModel):
    id: str
    email: str = Field(
        pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    fullName: str
    verified: bool
    banned: bool
    roles: list[Roles]
    createdAt: str

    @field_validator('createdAt')
    def validate_created_at(cls, value: str) -> str:
        try:
            datetime.datetime.fromisoformat(value)
        except ValueError:
            raise ValueError('Некорректный формат даты и времени')
        return value
