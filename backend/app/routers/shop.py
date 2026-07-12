from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import schemas, crud, models
from ..database import get_db
from .auth import get_current_user, get_current_admin

router = APIRouter(prefix="/shop", tags=["shop"])

@router.get("/items", response_model=List[schemas.ShopItemResponse])
async def read_shop_items(db: AsyncSession = Depends(get_db)):
    return await crud.get_shop_items(db)

@router.post("/buy/{item_id}")
async def buy_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    success, msg = await crud.buy_item(db, user_id=current_user.id, item_id=item_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@router.post("/equip/{user_item_id}")
async def equip_item(
    user_item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    success, msg = await crud.equip_item(db, user_id=current_user.id, user_item_id=user_item_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@router.get("/my-items", response_model=List[schemas.UserItemResponse])
async def read_my_items(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return await crud.get_user_items(db, user_id=current_user.id)

# ----------------- ADMIN -----------------
@router.post("/admin/items", response_model=schemas.ShopItemResponse)
async def create_shop_item(
    item: schemas.ShopItemCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    return await crud.create_shop_item(db=db, item=item)

@router.put("/admin/items/{item_id}", response_model=schemas.ShopItemResponse)
async def update_shop_item(
    item_id: str,
    item_update: schemas.ShopItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    updated = await crud.update_shop_item(db=db, item_id=item_id, item_update=item_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated

@router.delete("/admin/items/{item_id}")
async def delete_shop_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    success = await crud.delete_shop_item(db=db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"detail": "Item deleted"}
