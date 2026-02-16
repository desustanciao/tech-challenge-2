from fastapi import Depends, Cookie, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_token_from_header
from app.config import Settings, get_settings
from app.crud import ItemsCRUD, UserCRUD
from app.database import get_db


async def get_items_crud(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
) -> ItemsCRUD:
    """
    Dependency to provide a ItemsCRUD instance with DB session and settings.
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
    access_token: str | None = Cookie(default=None),
    token: str = Depends(get_token_from_header),
    users: UserCRUD = Depends(get_user_crud)
):
    """
    Validate JWT token and resolve user from DB.
    Raises 403 if token is invalid or user not found.
    """
    if not access_token and not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return await users.get_user_from_token(token)
