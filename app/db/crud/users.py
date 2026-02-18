import hashlib

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.auth import create_jwt, get_password_hash, validate_jwt, verify_password
from app.config import Settings
from app.db.models.users import User


# User
class UserCRUD:
    """
    Encapsulates all user-related database operations.
    Can be used as a dependency in FastAPI endpoints.
    """

    def __init__(self, db: AsyncSession, settings: Settings):
        self.db = db
        self.settings = settings

    async def get_by_username(self, username: str) -> User | None:
        """
        Get a user by username.
        :param username:
        :return:
        """
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        """
        Get a user by ID.
        :param user_id:
        :return:
        """
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, username: str, email: str, password: str) -> User:
        """
        Create a new user.
        :param username:
        :param email:
        :param password:
        :return:
        """
        hashed_password = get_password_hash(password)
        user = User(username=username, email=email, hashed_password=hashed_password)
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

    async def get_by_username_and_token(self, token: str, username: str) -> User | None:
        """
        Get a user by username and token.
        :param token:
        :param username:
        :return:
        """
        result = await self.db.execute(select(User).where(User.username == username, User.jwt_token == token))
        user = result.scalar_one_or_none()
        return user

    async def get_user_from_token(self, token: str) -> User:
        """
        Validate a JWT token against the database.
        Returns the User if valid, raises HTTPException otherwise.
        """
        username = await validate_jwt(token, self.settings)
        hashed_token = hashlib.sha256(token.encode()).hexdigest()
        user = await self.get_by_username_and_token(hashed_token, username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token",
            )

        return user

    async def generate_token_and_update_user(self, user: User) -> str:
        """
        Generates a new Token for the user
        :param user:
        :return:
        """
        encoded_jwt = create_jwt(user.username, self.settings)
        user.jwt_token = hashlib.sha256(encoded_jwt.encode()).hexdigest()

        await self.db.commit()
        return encoded_jwt

    async def remove_user_token(self, user: User) -> None:
        """
        remove token from user
        :param user:
        :return:
        """
        user.jwt_token = None
        await self.db.commit()
