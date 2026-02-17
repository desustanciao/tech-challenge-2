from pydantic import BaseModel, EmailStr, Field


class ItemBase(BaseModel):
    name: str
    description: str

    model_config = {"from_attributes": True}


class Item(ItemBase):
    id: int

    model_config = {"from_attributes": True}


class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr

    model_config = {"from_attributes": True}


class UserUpdate(UserBase):
    password: str = Field(..., min_length=8)
    jwt_token: str | None = Field(None)

    model_config = {"from_attributes": True}
