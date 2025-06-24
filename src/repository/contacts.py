from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Contact
from src.schemas.contact import ContactCreate, ContactUpdate
from datetime import date, timedelta


async def get_contacts(limit: int, offset: int, db: AsyncSession):
    stmt = select(Contact).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_contact_by_id(contact_id: int, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_contact_by_email(email: str, db: AsyncSession):
    stmt = select(Contact).filter_by(email=email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_contacts_by_first_name(first_name: str, db: AsyncSession):
    stmt = select(Contact).filter_by(first_name=first_name)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_contacts_by_last_name(last_name: str, db: AsyncSession):
    stmt = select(Contact).filter_by(last_name=last_name)
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_contact(body: ContactCreate, db: AsyncSession):
    contact = Contact(**body.model_dump(exclude_unset=True))
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdate, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        for key, value in body.model_dump(exclude_unset=True).items():
            setattr(contact, key, value)
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contact).filter_by(id=contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def get_upcoming_birthdays(db: AsyncSession):
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
