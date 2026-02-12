# app/dependencies.py
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_token_from_header
from app.config import get_settings, Settings
from app.crud import UserCRUD, ItemsCRUD
from app.database import get_db



async def get_items_crud(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
) -> ItemsCRUD:
    """
    Dependency to provide a UserCRUD instance with DB session and settings.
    """
    return ItemsCRUD(db, settings)


async def get_user_crud(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
) -> UserCRUD:
    """
    Dependency to provide a UserCRUD instance with DB session and settings.
    """
    return UserCRUD(db, settings)


async def get_current_user(
    token: str = Depends(get_token_from_header),
    users: UserCRUD = Depends(get_user_crud)
):
    """
    Validate JWT token and resolve user from DB.
    Raises 403 if token is invalid or user not found.
    """
    user = await users.validate_jwt(token)
    return user