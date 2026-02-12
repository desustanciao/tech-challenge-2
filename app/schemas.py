from pydantic import BaseModel, Field, EmailStr


class ItemBase(BaseModel):
    name: str
    description: str


class Item(ItemBase):
    id: int

    model_config = { "from_attributes": True}


class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr

    model_config = {
        "from_attributes": True  # enable ORM -> Pydantic conversion
    }


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    jwt_token: str | None = Field(None)


class UserUpdate(BaseModel):
    username: str | None = Field(None, max_length=50)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8)
    jwt_token: str | None = Field(None)

    model_config = {
        "from_attributes": True
    }