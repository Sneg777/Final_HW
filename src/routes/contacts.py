from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from src.repository import contacts as repo
from src.database.db import get_db

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(limit: int = 10, offset: int = 0, db: AsyncSession = Depends(get_db)):
    return await repo.get_contacts(limit, offset, db)


@router.get("/first_name/{first_name}", response_model=List[ContactResponse])
async def get_contacts_by_first_name(first_name: str, db: AsyncSession = Depends(get_db)):
    return await repo.get_contacts_by_first_name(first_name, db)


@router.get("/last_name/{last_name}", response_model=List[ContactResponse])
async def get_contacts_by_last_name(last_name: str, db: AsyncSession = Depends(get_db)):
    return await repo.get_contacts_by_last_name(last_name, db)


@router.get("/contact_id/{contact_id}", response_model=ContactResponse)
async def get_contact_by_id(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact = await repo.get_contact_by_id(contact_id, db)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.get("/email/{email}", response_model=ContactResponse)
async def get_contact_by_email(email: str, db: AsyncSession = Depends(get_db)):
    contact = await repo.get_contact_by_email(email, db)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactCreate, db: AsyncSession = Depends(get_db)):
    return await repo.create_contact(body, db)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, body: ContactUpdate, db: AsyncSession = Depends(get_db)):
    contact = await repo.update_contact(contact_id, body, db)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
    contact = await repo.delete_contact(contact_id, db)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")


@router.get("/upcoming-birthdays", response_model=List[ContactResponse])
async def upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    return await repo.get_upcoming_birthdays(db)
