import re
from pydantic import BaseModel, EmailStr, constr, validator, field_validator
from typing import Optional
from datetime import date


class ContactSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: constr()
    birthday: Optional[date]
    additional_data: Optional[str] = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v):
        if not re.match(r"^\+?1?\d{9,15}$", v):
            raise ValueError("Invalid phone number format")
        return v


class ContactUpdate(ContactSchema):
    pass


class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: constr()
    birthday: Optional[date]
    additional_data: Optional[str] = None
    user_id: int

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int = 1
    username: str
    email: EmailStr
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class RefreshToken(BaseModel):
    refresh_token: str
