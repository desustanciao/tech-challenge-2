from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Item, User
from app.auth import get_password_hash

async def init_db(db: AsyncSession):
    # 1️⃣ Check if items already exist
    result = await db.execute(select(Item))
    existing_item = result.scalars().first()
    if existing_item:
        return

    # 2️⃣ Add dummy items
    dummy_items = [
        Item(name="Item 1", description="Description 1"),
        Item(name="Item 2", description="Description 2"),
    ]
    db.add_all(dummy_items)

    # 3️⃣ Create a test user
    test_user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("password123")
    )
    db.add(test_user)

    # 4️⃣ Commit all changes
    await db.commit()