import bcrypt
from fastapi import Header, HTTPException, status


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
