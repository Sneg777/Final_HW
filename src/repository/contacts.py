from sqlalchemy import select
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Contact, User
from src.schemas.contact import ContactCreate, ContactUpdate
from datetime import date, timedelta


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    """
    Retrieve a paginated list of contacts for the current user.

    Args:
        limit (int): Maximum number of contacts to return.
        offset (int): Number of records to skip.
        db (AsyncSession): Database session.
        user (User): The current authenticated user.

    Returns:
        List[Contact]: List of user's contacts.
    """
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_contact_by_id(contact_id: int, db: AsyncSession, user: User):
    """
    Retrieve a contact by its ID for the current user.

    Args:
        contact_id (int): Contact ID.
        db (AsyncSession): Database session.
        user (User): The current authenticated user.

    Returns:
        Contact | None: Contact instance if found, else None.
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_contact_by_email(email: str, db: AsyncSession, user: User):
    """
    Retrieve a contact by email for the current user.

    Args:
        email (str): Contact's email.
        db (AsyncSession): Database session.
        user (User): The current authenticated user.

    Returns:
        Contact | None: Contact instance if found, else None.
    """
    stmt = select(Contact).filter_by(email=email, user=user)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_contacts_by_first_name(first_name: str, db: AsyncSession, user: User):
    """
    Retrieve contacts by first name for the current user.

    Args:
        first_name (str): First name to search for.
        db (AsyncSession): Database session.
        user (User): The current authenticated user.

    Returns:
        List[Contact]: List of matching contacts.
    """
    stmt = select(Contact).filter_by(first_name=first_name, user=user)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_contacts_by_last_name(last_name: str, db: AsyncSession, user: User):
    """
    Retrieve contacts by last name for the current user.

    Args:
        last_name (str): Last name to search for.
        db (AsyncSession): Database session.
        user (User): The current authenticated user.

    Returns:
        List[Contact]: List of matching contacts.
    """
    stmt = select(Contact).filter_by(last_name=last_name, user=user)
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_contact(body: ContactCreate, db: AsyncSession, user: User):
    """
    Create a new contact for the current user.

    Args:
        body (ContactCreate): Data for the new contact.
        db (AsyncSession): Database session.
        user (User): The current authenticated user.

    Returns:
        Contact: The created contact instance.

    Raises:
        HTTPException: If contact with the same email already exists.
    """
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
    """
    Update an existing contact for the current user.

    Args:
        contact_id (int): ID of the contact to update.
        body (ContactUpdate): Fields to update.
        db (AsyncSession): Database session.
        user (User): The current authenticated user.

    Returns:
        Contact | None: Updated contact if found, else None.
    """
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
    """
    Delete a contact by ID for the current user.

    Args:
        contact_id (int): ID of the contact to delete.
        db (AsyncSession): Database session.
        user (User): The current authenticated user.

    Returns:
        Contact | None: Deleted contact if found, else None.
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def get_upcoming_birthdays(db: AsyncSession, user: User):
    """
    Retrieve contacts with upcoming birthdays within the next 7 days.

    Args:
        db (AsyncSession): Database session.
        user (User): The current authenticated user.

    Returns:
        List[Contact]: List of contacts with upcoming birthdays.
    """
    today = date.today()
    next_week = today + timedelta(days=7)

    stmt = select(Contact).where(Contact.user_id == user.id)
    result = await db.execute(stmt)
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
