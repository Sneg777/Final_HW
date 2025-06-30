from sqlalchemy import select
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Contact, User
from src.schemas.contact import ContactCreate, ContactUpdate
from datetime import date, timedelta


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_contact_by_id(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_contact_by_email(email: str, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(email=email, user=user)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_contacts_by_first_name(first_name: str, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(first_name=first_name, user=user)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_contacts_by_last_name(last_name: str, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(last_name=last_name, user=user)
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_contact(body: ContactCreate, db: AsyncSession, user: User):
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    try:
        await db.commit()
        await db.refresh(contact)
        return contact
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Contact with this email already exists")


async def update_contact(contact_id: int, body: ContactUpdate, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(contact, key, value)
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def get_upcoming_birthdays(db: AsyncSession, user: User):  # TODO: user depends
    today = date.today()
    next_week = today + timedelta(days=7)

    result = await db.execute(select(Contact))
    contacts = result.scalars().all()

    upcoming_birthdays = []
    for contact in contacts:
        if contact.birthday:
            birthday_this_year = contact.birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            if today <= birthday_this_year <= next_week:
                upcoming_birthdays.append(contact)

    return upcoming_birthdays
