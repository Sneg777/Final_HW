import unittest
from unittest.mock import AsyncMock, MagicMock
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactCreate, ContactUpdate
from src.repository.contacts import get_contact_by_id, get_contact_by_email, get_contacts, get_contacts_by_last_name, \
    get_contacts_by_first_name, get_upcoming_birthdays, update_contact, delete_contact, create_contact


class TestAsyncContactsRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.User = User(id=1, username='test_user', password="qwerty", confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(id=1, first_name="Alice", last_name="Smith", email="alice@example.com", user=self.User),
            Contact(id=2, first_name="Bob", last_name="Jones", email="bob@example.com", user=self.User),
        ]

        mocked_scalars = MagicMock()
        mocked_scalars.all.return_value = contacts

        mocked_result = MagicMock()
        mocked_result.scalars.return_value = mocked_scalars

        self.session.execute.return_value = mocked_result

        result = await get_contacts(limit, offset, self.session, self.User)
        self.assertEqual(result, contacts)

    async def test_get_contact_by_id(self):
        contact = Contact(id=1, user=self.User)
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_result

        result = await get_contact_by_id(1, self.session, self.User)
        self.assertEqual(result, contact)

    async def test_get_contact_by_email(self):
        contact = Contact(id=1, email="test@example.com", user=self.User)
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_result

        result = await get_contact_by_email("test@example.com", self.session, self.User)
        self.assertEqual(result, contact)

    async def test_get_contacts_by_first_name(self):
        contacts = [Contact(id=1, first_name="John", user=self.User)]
        mocked_scalars = MagicMock()
        mocked_scalars.all.return_value = contacts

        mocked_result = MagicMock()
        mocked_result.scalars.return_value = mocked_scalars

        self.session.execute.return_value = mocked_result

        result = await get_contacts_by_first_name("John", self.session, self.User)
        self.assertEqual(result, contacts)

    async def test_get_contacts_by_last_name(self):
        contacts = [Contact(id=1, last_name="Doe", user=self.User)]
        mocked_scalars = MagicMock()
        mocked_scalars.all.return_value = contacts

        mocked_result = MagicMock()
        mocked_result.scalars.return_value = mocked_scalars

        self.session.execute.return_value = mocked_result

        result = await get_contacts_by_last_name("Doe", self.session, self.User)
        self.assertEqual(result, contacts)

    async def test_create_contact(self):
        body = ContactCreate(first_name="Jane", last_name="Smith", email="jane@example.com")
        result = await create_contact(body, self.session, self.User)
        self.assertEqual(result.first_name, body.first_name)

    async def test_update_contact(self):
        contact = Contact(id=1, first_name="Old", user=self.User)
        update_data = ContactUpdate(first_name="New", last_name="Smith", email="old@example.com")

        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_result

        result = await update_contact(1, update_data, self.session, self.User)
        self.assertEqual(result.first_name, "New")

    async def test_delete_contact(self):
        contact = Contact(id=1, user=self.User)

        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_result

        result = await delete_contact(1, self.session, self.User)
        self.assertIsInstance(result, Contact)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertEqual(result, contact)

    async def test_get_upcoming_birthdays(self):
        today = date.today()
        next_week = today + timedelta(days=7)

        contact = Contact(id=1, birthday=today, user=self.User)

        mocked_scalars = MagicMock()
        mocked_scalars.all.return_value = [contact]
        mocked_result = MagicMock()
        mocked_result.scalars.return_value = mocked_scalars

        self.session.execute.return_value = mocked_result

        result = await get_upcoming_birthdays(self.session, self.User)
        self.assertIn(contact, result)
