from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt
from app.config import settings

security = HTTPBearer()

def verify_token(credentials=Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication token"
        )
