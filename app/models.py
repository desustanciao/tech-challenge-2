from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    pass

class Item(Base):
    __tablename__ = "items"

    id = mapped_column(Integer, primary_key=True, index=True)
    name = mapped_column(String, nullable=False, index=True)
    description = mapped_column(String)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    jwt_token: Mapped[str] = mapped_column(String, nullable=True)
