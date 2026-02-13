import os
import asyncio
from unittest.mock import AsyncMock

import pytest

from httpx import AsyncClient, ASGITransport
from jose import jwt
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.auth import get_password_hash
from app.main import app
from app.database import get_db
from app.config import Settings
from app.models import Item, Base, User


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
def access_token(mock_settings):
    return jwt.encode(
        {"sub": "testuser"},
        mock_settings.SECRET_KEY,
        algorithm=mock_settings.ALGORITHM,
    )

@pytest.fixture
def mock_items_crud():
    class MockItemsCRUD:
        async def get_items(self):
            return [Item(id=1, name="Test", description="I Will get the job!")]

    return MockItemsCRUD()

@pytest.fixture(autouse=True)
def override_items_crud(mock_items_crud):
    from app.dependencies import get_items_crud

    app.dependency_overrides[get_items_crud] = lambda: mock_items_crud
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def mock_user_crud():
    class MockUserCRUD:
        async def validate_jwt(self, token):
            test_user = User(
                username="testuser",
                email="test@example.com",
                hashed_password=get_password_hash("password123")
            )
            return test_user

    return MockUserCRUD()

@pytest.fixture(autouse=True)
def override_users_crud(mock_user_crud):
    from app.dependencies import get_user_crud

    app.dependency_overrides[get_user_crud] = lambda: mock_user_crud
    yield
    app.dependency_overrides.clear()