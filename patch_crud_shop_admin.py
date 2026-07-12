import re

with open('backend/app/crud.py', 'r', encoding='utf-8') as f:
    crud = f.read()

shop_admin_logic = """
async def create_shop_item(db: AsyncSession, item: schemas.ShopItemCreate):
    db_item = models.ShopItem(**item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def update_shop_item(db: AsyncSession, item_id: str, item_update: schemas.ShopItemUpdate):
    result = await db.execute(select(models.ShopItem).filter(models.ShopItem.id == item_id))
    db_item = result.scalars().first()
    if not db_item:
        return None
        
    update_data = item_update.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
        
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def delete_shop_item(db: AsyncSession, item_id: str):
    result = await db.execute(select(models.ShopItem).filter(models.ShopItem.id == item_id))
    db_item = result.scalars().first()
    if db_item:
        await db.delete(db_item)
        await db.commit()
        return True
    return False
"""

if "def create_shop_item" not in crud:
    crud += "\n" + shop_admin_logic
    
    with open('backend/app/crud.py', 'w', encoding='utf-8') as f:
        f.write(crud)
    print("Added shop admin logic to crud.py")
else:
    print("Already added")
