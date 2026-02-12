from typing import Any

from fastapi import HTTPException
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth import get_password_hash, verify_password
from app.config import Settings
from app.models import Item, User


# Item
class ItemsCRUD:
    def __init__(self, db: AsyncSession, settings: Settings):
        self.db = db
        self.settings = settings
    async def get_items(self):
        result = await self.db.execute(select(Item))
        return result.scalars().all()

# User


class UserCRUD:
    """
    Encapsulates all user-related database operations.
    Can be used as a dependency in FastAPI endpoints.
    """

    def __init__(self, db: AsyncSession, settings: Settings):
        self.db = db
        self.settings = settings

    # ----------------------
    # Read operations
    # ----------------------
    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    # ----------------------
    # Create / Authenticate
    # ----------------------
    async def create(self, username: str, email: str, password: str) -> User:
        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate_password(self, username: str, password: str) -> User | None:
        """
        Verify username and password. Return User if valid, else None.
        """
        user = await self.get_by_username(username)
        if not user:
            return None
        if verify_password(password, user.hashed_password):
            return user
        return None

    async def get_by_username_and_token(self, token: str, username: str) -> Any | None:
        result = await self.db.execute(
            select(User).where(User.username == username, User.jwt_token == token)
        )
        user = result.scalar_one_or_none()
        return user

    async def validate_jwt(self, token: str) -> User | None:
        """
        Validate a JWT token against the database.
        Returns the User if valid, raises HTTPException otherwise.
        """
        try:
            # Decode token to get payload
            payload = jwt.decode(
                token,
                self.settings.SECRET_KEY,
                algorithms=[self.settings.ALGORITHM]
            )
            username: str = payload.get("sub")
            if not username:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid JWT payload",
                )

            # Query user by username AND matching token in DB
            user = await self.get_by_username_and_token(token, username)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Token not recognized",
                )

            return user

        except JWTError as err:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authentication token",
            ) from err

