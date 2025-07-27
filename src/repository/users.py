from fastapi import Depends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema
from src.services.cloudinary import upload_avatar


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a user from the database by email.

    Args:
        email (str): The email of the user to search for.
        db (AsyncSession): The database session (injected).

    Returns:
        User | None: The user object if found, otherwise None.
    """
    stmt = select(User).where(User.email == email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    Create a new user in the database.

    Args:
        body (UserSchema): The user data for creation.
        db (AsyncSession): The database session (injected).

    Returns:
        User: The newly created user.
    """
    avatar = None
    try:
        avatar = await upload_avatar('default_avatar.png', public_id=body.email)
    except Exception as err:
        print(err)

    new_user = User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    Update the user's refresh token.

    Args:
        user (User): The user to update.
        token (str | None): The new refresh token.
        db (AsyncSession): The database session.
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Mark a user's email as confirmed.

    Args:
        email (str): The email of the user to confirm.
        db (AsyncSession): The database session.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar(user: User, avatar_url: str, db: AsyncSession) -> User:
    """
    Update a user's avatar URL.

    Args:
        user (User): The user to update.
        avatar_url (str): The new avatar URL.
        db (AsyncSession): The database session.

    Returns:
        User: The updated user instance.
    """
    user.avatar = avatar_url
    await db.commit()
    await db.refresh(user)
    return user
