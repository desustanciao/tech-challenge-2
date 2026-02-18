import datetime
from datetime import timedelta

import bcrypt
import jwt
from fastapi import Cookie, Header, HTTPException, status
from jwt import PyJWTError

from app.config import Settings


def get_password_hash(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    Returns a UTF-8 encoded string.
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


async def get_token_from_request(
    authorization: str | None = Header(None, description="Bearer JWT token"),
    access_token: str | None = Cookie(None),
) -> str:
    """
    Extract token from Authorization header or cookie.
    Header takes priority if present.
    """
    token: str | None = None

    if authorization:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authorization header")
        token = authorization[len("Bearer ") :]

    elif access_token:
        token = access_token

    if not token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")

    return token


def create_jwt(
    username: str,
    settings: Settings,
) -> str:
    """
    Create a JWT hash using a username.
    :param username:
    :param settings:
    :return:
    """

    expire = datetime.datetime.now(datetime.UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": username,
        "exp": expire,
        "iat": datetime.datetime.now(datetime.UTC),
    }
    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    return encoded_jwt


async def validate_jwt(token: str, settings) -> str:
    """
    Validate a JWT token and returns the username
    :param token:
    :param settings:
    :return:
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except PyJWTError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication token",
        ) from err

    username: str = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid JWT payload",
        )
    return username
