from sqlalchemy.orm import Session
from app.models import Item

def init_db(db: Session):
    if db.query(Item).first():
        return

    dummy_items = [
        Item(name="Item 1", description="Description 1"),
        Item(name="Item 2", description="Description 2"),
    ]
    db.add_all(dummy_items)
    db.commit()
