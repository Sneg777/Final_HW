from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from sqlalchemy import String, Date
from sqlalchemy.orm import DeclarativeBase
from typing import Optional


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    birthday: Mapped[date] = mapped_column(Date)
    additional_data: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
