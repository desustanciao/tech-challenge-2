from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column

from app.db.models.base import Base


class Item(Base):
    __tablename__ = "items"

    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, nullable=False, index=True)
    description = mapped_column(String)
