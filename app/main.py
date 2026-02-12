from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.auth import verify_token
from app.database import Base, engine, get_db
from app.logging_config import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
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
async def readiness(db: AsyncSession = get_db):
    await db.execute("SELECT 1")
    return {"status": "ready"}


@app.get("/items", response_model=list[schemas.Item])
async def read_items(db: AsyncSession = get_db, user=verify_token):
    return await crud.get_items(db)
