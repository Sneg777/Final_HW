from fastapi import APIRouter, Depends, HTTPException, status, Security, BackgroundTasks, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse
from src.schemas.user import UserSchema, TokenSchema, UserResponse, RequestEmail
from src.repository import users as repositories_users
from src.database.db import get_db
from src.services.auth import auth_service
from src.services.email import send_email
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/auth", tags=["auth"])
get_refresh_token = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account.

    Sends a confirmation email after creating the user.

    Args:
        body (UserSchema): User data for registration.
        bt (BackgroundTasks): Background task handler for sending email.
        request (Request): Current HTTP request.
        db (AsyncSession): SQLAlchemy async session.

    Returns:
        UserResponse: The newly created user object.

    Raises:
        HTTPException: If an account with the given email already exists.
    """
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenSchema, status_code=status.HTTP_200_OK,
             dependencies=[Depends(RateLimiter(times=5, seconds=20))])
async def login(body: OAuth2PasswordRequestForm = Depends(),
                db: AsyncSession = Depends(get_db)):
    """
    Authenticate a user and return JWT tokens.

    Args:
        body (OAuth2PasswordRequestForm): User credentials (email and password).
        db (AsyncSession): SQLAlchemy async session.

    Returns:
        TokenSchema: Dictionary with access token, refresh token, and token type.

    Raises:
        HTTPException: For invalid email, unconfirmed email, or wrong password.
    """
    user = await repositories_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenSchema, status_code=status.HTTP_200_OK,
            dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    """
    Generate new JWT tokens using a valid refresh token.

    Args:
        credentials (HTTPAuthorizationCredentials): Bearer token from the request header.
        db (AsyncSession): SQLAlchemy async session.

    Returns:
        TokenSchema: Dictionary with new access token, refresh token, and token type.

    Raises:
        HTTPException: If the refresh token is invalid.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirm a user's email based on the verification token.

    Args:
        token (str): Email verification token.
        db (AsyncSession): SQLAlchemy async session.

    Returns:
        dict: Message indicating whether the email was confirmed or already confirmed.

    Raises:
        HTTPException: If verification fails or user does not exist.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repositories_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    Request a new confirmation email.

    Args:
        body (RequestEmail): Object containing the user's email.
        background_tasks (BackgroundTasks): FastAPI background task handler.
        request (Request): Current HTTP request.
        db (AsyncSession): SQLAlchemy async session.

    Returns:
        dict: Message prompting the user to check their email.

    Raises:
        HTTPException: If user is not found or email already confirmed.
    """
    user = await repositories_users.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.confirmed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Your email is already confirmed")
    background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}
