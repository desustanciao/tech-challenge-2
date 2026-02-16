from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Response
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app import schemas
from app.config import get_settings
from app.crud import ItemsCRUD, UserCRUD
from app.database import get_db
from app.dependencies import get_current_user, get_items_crud, get_user_crud
from app.logging_config import configure_logging
from app.models import Base, User


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()  # ✅ call directly, no Depends
    db_url = (
        f"postgresql+psycopg://{settings.DATABASE_USER}:"
        f"{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:5432/"
        f"{settings.DATABASE_NAME}?sslmode=require"
    )

    engine = create_async_engine(db_url, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    yield


app = FastAPI(title="challenge", lifespan=lifespan)

configure_logging()

Instrumentator().instrument(app).expose(app)


@app.get("/health/live")
async def liveness():
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "ready"}


@app.get("/items", response_model=list[schemas.Item])
async def read_items(items: ItemsCRUD = Depends(get_items_crud), current_user: User = Depends(get_current_user)):
    return await items.get_items()


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
    user_crud: UserCRUD = Depends(get_user_crud)
):
    if current_user:
        await user_crud.remove_user_token(current_user)

    response.delete_cookie("access_token")

    return {"message": "Logged out"}