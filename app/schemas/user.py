from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(UserBase):
    password: str = Field(..., min_length=8)
    jwt_token: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
