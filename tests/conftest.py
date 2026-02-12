import os
import asyncio
from unittest.mock import AsyncMock

import pytest

from httpx import AsyncClient, ASGITransport
from jose import jwt
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app import crud
from app.crud import ItemsCRUD
from app.main import app
from app.database import get_db
from app.config import Settings
from app.models import Item, Base


@pytest.fixture(scope="session")
def mock_settings():
    """
    Replace the real Settings with test values.
    Automatically used in all tests.
    """
    test_settings = Settings(
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        SECRET_KEY="testsecret",
        ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=30
    )
    yield test_settings

@pytest.fixture(autouse=True)
def override_settings(mock_settings):
    from app.config import get_settings

    app.dependency_overrides[get_settings] = lambda: mock_settings
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine(mock_settings):
    engine = create_async_engine(
        mock_settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(engine):
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session


@pytest.fixture(autouse=True)
def override_get_db(db_session):
    async def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def mock_db_session(monkeypatch):
    class DummySession:
        async def execute(self, query, *args, **kwargs):
            class DummyResult:
                def scalars(self):
                    return []
            return DummyResult()

    session = DummySession()
    monkeypatch.setattr(crud, "get_items", lambda db: [Item(id=1, name="Test", description="Test desc")])
    yield session


@pytest.fixture
def access_token(mock_settings):
    return jwt.encode(
        {"sub": "testuser"},
        mock_settings.SECRET_KEY,
        algorithm=mock_settings.ALGORITHM,
    )