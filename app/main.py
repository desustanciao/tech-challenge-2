from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Response
from prometheus_client import make_asgi_app
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.db.crud.users import UserCRUD
from app.db.database import get_db
from app.db.init_db import init_db
from app.db.models.base import Base
from app.db.models.users import User
from app.dependencies import get_current_user, get_user_crud
from app.items.router import items_router
from app.logging_config import configure_logging
from app.metrics.prometheus import prometheus_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    sslmode = "disable" if settings.LOCAL else "require"
    db_url = (
        f"postgresql+psycopg://{settings.DATABASE_USER}:"
        f"{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:5432/"
        f"{settings.DATABASE_NAME}?sslmode={sslmode}"
    )

    engine = create_async_engine(db_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        await init_db(session)
    await engine.dispose()
    yield


app = FastAPI(title="challenge", lifespan=lifespan)

configure_logging()

app.middleware("http")(prometheus_middleware)
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health/live")
async def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "ready"}


@app.post("/get_token")
async def get_token(username: str, user_crud: UserCRUD = Depends(get_user_crud)):
    user = await user_crud.get_by_username(username)
    token = await user_crud.generate_token_and_update_user(user)

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@app.get("/get_cookie")
async def get_cookie(response: Response, username: str, user_crud: UserCRUD = Depends(get_user_crud)):
    user = await user_crud.get_by_username(username)
    token = await user_crud.generate_token_and_update_user(user)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60,
        path="/",
    )
    return {"message": "Login successful"}


@app.get("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    user_crud: UserCRUD = Depends(get_user_crud),
):
    if current_user:
        await user_crud.remove_user_token(current_user)

    response.delete_cookie("access_token")

    return {"message": "Logged out"}


app.include_router(items_router)
