from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.services.auth import auth_service
from src.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from src.repository import contacts as repo
from src.database.db import get_db
from src.entity.models import User
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse], dependencies=[Depends(RateLimiter(times=10, seconds=20))])
async def read_contacts(limit: int = 10, offset: int = 0, db: AsyncSession = Depends(get_db),
                        user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve a list of contacts for the authenticated user.

    Args:
        limit (int): Number of contacts to return.
        offset (int): Number of contacts to skip.
        db (AsyncSession): SQLAlchemy async session.
        user (User): Current authenticated user.

    Returns:
        List[ContactResponse]: List of contact objects.
    """
    return await repo.get_contacts(limit, offset, db, user)


@router.get("/first_name/{first_name}", response_model=List[ContactResponse], dependencies=[Depends(RateLimiter(times=3, seconds=20))])
async def get_contacts_by_first_name(first_name: str, db: AsyncSession = Depends(get_db),
                                     user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve contacts by first name.

    Args:
        first_name (str): Contact's first name.
        db (AsyncSession): SQLAlchemy async session.
        user (User): Current authenticated user.

    Returns:
        List[ContactResponse]: List of contact objects.
    """
    return await repo.get_contacts_by_first_name(first_name, db, user)


@router.get("/last_name/{last_name}", response_model=List[ContactResponse], dependencies=[Depends(RateLimiter(times=3, seconds=20))])
async def get_contacts_by_last_name(last_name: str, db: AsyncSession = Depends(get_db),
                                    user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve contacts by last name.

    Args:
        last_name (str): Contact's last name.
        db (AsyncSession): SQLAlchemy async session.
        user (User): Current authenticated user.

    Returns:
        List[ContactResponse]: List of contact objects.
    """
    return await repo.get_contacts_by_last_name(last_name, db, user)


@router.get("/contact_id/{contact_id}", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=3, seconds=20))])
async def get_contact_by_id(contact_id: int, db: AsyncSession = Depends(get_db),
                            user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve a contact by its ID.

    Args:
        contact_id (int): Contact ID.
        db (AsyncSession): SQLAlchemy async session.
        user (User): Current authenticated user.

    Returns:
        ContactResponse: The contact object.

    Raises:
        HTTPException: If contact is not found.
    """
    contact = await repo.get_contact_by_id(contact_id, db, user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.get("/email/{email}", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=3, seconds=20))])
async def get_contact_by_email(email: str, db: AsyncSession = Depends(get_db),
                               user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve a contact by its email.

    Args:
        email (str): Contact email.
        db (AsyncSession): SQLAlchemy async session.
        user (User): Current authenticated user.

    Returns:
        ContactResponse: The contact object.

    Raises:
        HTTPException: If contact is not found.
    """
    contact = await repo.get_contact_by_email(email, db, user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=3, seconds=20))])
async def create_contact(body: ContactCreate, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    Create a new contact.

    Args:
        body (ContactCreate): Contact data.
        db (AsyncSession): SQLAlchemy async session.
        user (User): Current authenticated user.

    Returns:
        ContactResponse: The newly created contact object.
    """
    return await repo.create_contact(body, db, user)


@router.put("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=3, seconds=20))])
async def update_contact(contact_id: int, body: ContactUpdate, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    Update an existing contact.

    Args:
        contact_id (int): ID of the contact to update.
        body (ContactUpdate): Updated contact data.
        db (AsyncSession): SQLAlchemy async session.
        user (User): Current authenticated user.

    Returns:
        ContactResponse: The updated contact object.

    Raises:
        HTTPException: If contact is not found.
    """
    contact = await repo.update_contact(contact_id, body, db, user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RateLimiter(times=3, seconds=20))])
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    Delete a contact.

    Args:
        contact_id (int): ID of the contact to delete.
        db (AsyncSession): SQLAlchemy async session.
        user (User): Current authenticated user.

    Raises:
        HTTPException: If contact is not found.
    """
    contact = await repo.delete_contact(contact_id, db, user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")


@router.get("/upcoming-birthdays", response_model=List[ContactResponse], dependencies=[Depends(RateLimiter(times=3, seconds=20))])
async def upcoming_birthdays(db: AsyncSession = Depends(get_db),
                             user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve contacts with birthdays in the upcoming 7 days.

    Args:
        db (AsyncSession): SQLAlchemy async session.
        user (User): Current authenticated user.

    Returns:
        List[ContactResponse]: List of contacts with upcoming birthdays.
    """
    return await repo.get_upcoming_birthdays(db, user)
