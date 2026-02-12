from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt

from app.config import get_settings, Settings
from app.dependencies import get_security


def verify_token(
        credentials: HTTPAuthorizationCredentials = get_security,
        settings: Settings = get_settings
                 ):
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication token"
        ) from err
