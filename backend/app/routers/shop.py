from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import schemas, crud, models
from ..database import get_db
from .auth import get_current_user, get_current_admin

router = APIRouter(prefix="/shop", tags=["shop"])

from ..seed_shop import seed_shop
from ..update_icons import update

@router.get("/seed_manual")
async def seed_manual():
    try:
        await seed_shop()
        await update()
        return {"status": "ok", "message": "Seeded and updated icons successfully"}
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "trace": traceback.format_exc()}

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

@router.delete("/admin/items/clear_all")
async def clear_all_shop_items(
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    from sqlalchemy import delete
    await db.execute(delete(models.UserItem))
    await db.execute(delete(models.ShopItem))
    await db.commit()
    return {"detail": "All items deleted"}

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
