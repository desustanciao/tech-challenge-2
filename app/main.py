from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine, Base, get_db
from app import crud, schemas
from app.auth import verify_token
from app.logging_config import configure_logging
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="FastAPI AWS App")

configure_logging()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

Instrumentator().instrument(app).expose(app)

@app.get("/health/live")
async def liveness():
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness(db: AsyncSession = Depends(get_db)):
    await db.execute("SELECT 1")
    return {"status": "ready"}

@app.get("/items", response_model=list[schemas.Item])
async def read_items(
    db: AsyncSession = Depends(get_db),
    user=Depends(verify_token)
):
    return await crud.get_items(db)
