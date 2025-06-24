from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date


class ContactBase(BaseModel):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    birthday: Optional[date]
    additional_data: Optional[str] = Field(None, max_length=200)

    class Config:
        from_attributes = True


class ContactCreate(ContactBase):
    pass


class ContactUpdate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: int

