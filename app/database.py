from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from app.config import Settings, get_settings


def get_engine(settings: Settings = Depends(get_settings), sslmode: str = "require") -> AsyncEngine:
    """
    return postgres engine instance
    :param sslmode:
    :param settings:
    :return:
    """
    if settings.LOCAL:
        sslmode = "disable"
    db_url = f"postgresql+psycopg://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:5432/{settings.DATABASE_NAME}?sslmode={sslmode}"
    return create_async_engine(
        db_url,
        echo=False,
    )


def get_sessionmaker(engine: AsyncEngine = Depends(get_engine)) -> async_sessionmaker:
    """
    return sessionmaker instance
    :param engine:
    :return:
    """
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_db(sessionmaker: async_sessionmaker = Depends(get_sessionmaker)) -> AsyncGenerator[AsyncSession]:
    """
    return session instance
    :param sessionmaker:
    :return:
    """
    async with sessionmaker() as session:
        yield session
