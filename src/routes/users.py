from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File

from src.repository import users as repository_users
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.auth import auth_service
from src.schemas.user import UserResponse
from src.database.db import get_db
from src.entity.models import User
from fastapi_limiter.depends import RateLimiter
import cloudinary.uploader

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    return user


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(
        file: UploadFile = File(...),
        current_user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db),
):
    try:
        file_content = await file.read()
        result = cloudinary.uploader.upload(
            file_content,
            public_id=current_user.email,
            folder="avatars",
            overwrite=True,
            resource_type="image"
        )

        avatar_url = result.get("secure_url")
        user = await repository_users.update_avatar(current_user, avatar_url, db)
        return user

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
