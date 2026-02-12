from fastapi import HTTPException, status, Header, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

from app.config import get_settings, Settings
import bcrypt


security = HTTPBearer()

def get_security() -> HTTPAuthorizationCredentials:
    return Depends(security)

def get_password_hash(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    The salt is automatically generated and stored in the hash.
    Returns a UTF-8 encoded string.
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a bcrypt hash.
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

async def get_token_from_header(
    authorization: str = Header(..., description="Bearer JWT token")
) -> str:
    """
    Extracts the token from the Authorization header.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authorization header"
        )
    return authorization[len("Bearer "):]


async def verify_token(
        credentials: HTTPAuthorizationCredentials = get_security,
        settings: Settings = get_settings,
):
    try:
        # 1. Decode the JWT
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication token"
            )

        # 2. Query the database for the user
        user = get_user_by_username(username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="User not found"
            )

        # 3. Return user or payload as needed
        return user
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication token"
        ) from err
