import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.schemas.user import UserSchema
from src.repository.users import get_user_by_email, create_user, update_token, confirmed_email, update_avatar


class TestAsyncUserRepository(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.user = User(id=1, username='test_user', email='test@example.com', password='hashed', confirmed=False)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_user_by_email(self):
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocked_result

        result = await get_user_by_email('test@example.com', self.session)
        self.assertEqual(result, self.user)

    @patch("src.repository.users.upload_avatar", new_callable=AsyncMock)
    async def test_create_user(self, mock_upload_avatar):
        mock_upload_avatar.return_value = "http://mocked.avatar.url"

        user_data = UserSchema(
            username='newuser',
            email='newuser@example.com',
            password='qwerty12'
        )

        self.session.add = MagicMock()
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()

        result = await create_user(user_data, self.session)

        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()
        self.assertEqual(result.username, user_data.username)
        self.assertEqual(result.avatar, "http://mocked.avatar.url")

    async def test_update_token(self):
        token = "new_refresh_token"
        await update_token(self.user, token, self.session)

        self.assertEqual(self.user.refresh_token, token)
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocked_result

        await confirmed_email(self.user.email, self.session)

        self.assertTrue(self.user.confirmed)
        self.session.commit.assert_called_once()

    async def test_update_avatar(self):
        new_avatar = "http://new.avatar.url"
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()

        result = await update_avatar(self.user, new_avatar, self.session)

        self.assertEqual(self.user.avatar, new_avatar)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(self.user)
        self.assertEqual(result, self.user)
