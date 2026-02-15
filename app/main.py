from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.crud import ItemsCRUD
from app.database import get_db, get_engine
from app.dependencies import get_current_user, get_items_crud
from app.logging_config import configure_logging
from app.models import Base, User


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Tech-challenge", lifespan=lifespan)

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
