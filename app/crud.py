from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Item

async def get_items(db: AsyncSession):
    result = await db.execute(select(Item))
    return result.scalars().all()
