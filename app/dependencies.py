# app/dependencies.py
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()


def get_security() -> HTTPAuthorizationCredentials:
    return Depends(security)
