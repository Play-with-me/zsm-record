import re

# 1. Update crud.py to delete related user items
c = open('backend/app/crud.py', 'r', encoding='utf-8').read()

# Find delete_shop_item and add the cascade delete
old_func = """async def delete_shop_item(db: AsyncSession, item_id: str):
    result = await db.execute(select(models.ShopItem).filter(models.ShopItem.id == item_id))
    db_item = result.scalars().first()
    if db_item:
        await db.delete(db_item)
        await db.commit()
        return True
    return False"""

new_func = """async def delete_shop_item(db: AsyncSession, item_id: str):
    from sqlalchemy import delete
    result = await db.execute(select(models.ShopItem).filter(models.ShopItem.id == item_id))
    db_item = result.scalars().first()
    if db_item:
        # Manually cascade delete user items first
        await db.execute(delete(models.UserItem).where(models.UserItem.item_id == item_id))
        await db.delete(db_item)
        await db.commit()
        return True
    return False"""

c = c.replace(old_func, new_func)
open('backend/app/crud.py', 'w', encoding='utf-8').write(c)

# 2. Update main.py to stop calling seed_shop
m = open('backend/app/main.py', 'r', encoding='utf-8').read()
m = m.replace("await seed_shop.seed_shop()", "# await seed_shop.seed_shop()  # Disabled to prevent auto-restoring deleted items")
open('backend/app/main.py', 'w', encoding='utf-8').write(m)
