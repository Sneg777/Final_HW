from datetime import datetime, timedelta, timezone # Убедимся, что timezone импортирован
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import config


class Auth:
    """
    Authentication service handling password hashing, JWT tokens creation and validation.

    Attributes:
        pwd_context: Password hashing context
        SECRET_KEY: Secret key for JWT (from config)
        ALGORITHM: Algorithm for JWT (from config)
        oauth2_scheme: OAuth2 password bearer scheme
    :noindex:
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config.SECRET_KEY
    ALGORITHM = config.ALGORITHM
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    def verify_password(self, plain_password, hashed_password):
        """
        Verify a plain password against a hashed password.

        Args:
            plain_password: Password in plain text
            hashed_password: Hashed password to compare against

        Returns:
            bool: True if passwords match, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Generate a hashed version of the password.

        Args:
            password: Password in plain text

        Returns:
            str: Hashed password
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create a JWT access token.

        Args:
            data: Dictionary containing token claims (typically user email)
            expires_delta: Optional expiration time in seconds

        Returns:
            str: Encoded JWT access token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta) # ИСПРАВЛЕНО
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15) # ИСПРАВЛЕНО
        to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "access_token"}) # ИСПРАВЛЕНО
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create a JWT refresh token.

        Args:
            data: Dictionary containing token claims (typically user email)
            expires_delta: Optional expiration time in seconds

        Returns:
            str: Encoded JWT refresh token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire, "scope": "refresh_token"}) # ИСПРАВЛЕНО
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Decode and validate a refresh token.

        Args:
            refresh_token: JWT refresh token string

        Returns:
            str: Email extracted from token

        Raises:
            HTTPException: 401 if token is invalid or has wrong scope
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        """
        Get current authenticated user from access token.

        Args:
            token: JWT access token
            db: Async database session

        Returns:
            User: Authenticated user object

        Raises:
            HTTPException: 401 if token is invalid or user not found
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

    def create_email_token(self, data: dict):
        """
        Create a token for email verification.

        Args:
            data: Dictionary containing token claims (typically user email)

        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=1)
        to_encode.update({"iat": datetime.now(timezone.utc), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        Extract email from verification token.

        Args:
            token: JWT token string

        Returns:
            str: Email extracted from token

        Raises:
            HTTPException: 422 if token is invalid
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid token")


auth_service = Auth()
