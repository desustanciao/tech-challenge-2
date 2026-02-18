from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db.models.items import Item


class ItemsCRUD:
    def __init__(self, db: AsyncSession, settings: Settings):
        self.db = db
        self.settings = settings

    async def get_items(self):
        result = await self.db.execute(select(Item))
        return result.scalars().all()
