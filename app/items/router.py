from fastapi import APIRouter, Depends

from app.auth import get_token_from_request
from app.db.crud.items import ItemsCRUD
from app.dependencies import get_items_crud
from app.items.item import Item

items_router = APIRouter(tags=["Items"], dependencies=[Depends(get_token_from_request)])


@items_router.get("/items", response_model=list[Item])
async def read_items(items: ItemsCRUD = Depends(get_items_crud)):
    return await items.get_items()
