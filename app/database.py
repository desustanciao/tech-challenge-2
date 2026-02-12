from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from app.config import get_settings

Base = declarative_base()


def get_engine():
    settings = get_settings()
    return create_async_engine(settings.DATABASE_URL, echo=False)


def get_sessionmaker():
    engine = get_engine()
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        yield session
