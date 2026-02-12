from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.auth import verify_token
from app.database import Base, get_db, get_engine
from app.logging_config import configure_logging


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
async def read_items(db: AsyncSession = Depends(get_db), user=Depends(verify_token)):
    return await crud.get_items(db)
