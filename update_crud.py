import re

with open('backend/app/crud.py', 'r', encoding='utf-8') as f:
    crud = f.read()

# 1. Update create_video to give coins
crud = crud.replace('user.exp += 50', 'user.exp += 50\n        user.coins += 20')

# 2. Add Shop functions at the end
shop_functions = """
# ---------------- SHOP & INVENTORY ----------------
async def get_shop_items(db: AsyncSession):
    result = await db.execute(select(models.ShopItem))
    return result.scalars().all()

async def get_user_items(db: AsyncSession, user_id: str):
    result = await db.execute(
        select(models.UserItem)
        .options(selectinload(models.UserItem.item))
        .filter(models.UserItem.user_id == user_id)
    )
    return result.scalars().all()

async def buy_item(db: AsyncSession, user_id: str, item_id: str):
    user = await db.get(models.User, user_id)
    item = await db.get(models.ShopItem, item_id)
    
    if not user or not item:
        return False, "User or Item not found"
        
    # Check if user already owns it
    result = await db.execute(
        select(models.UserItem)
        .filter(models.UserItem.user_id == user_id, models.UserItem.item_id == item_id)
    )
    if result.scalar_one_or_none():
        return False, "Bạn đã sở hữu vật phẩm này rồi"
        
    if user.coins < item.price:
        return False, "Không đủ Z-Coins"
        
    user.coins -= item.price
    user_item = models.UserItem(user_id=user_id, item_id=item_id, is_equipped=False)
    db.add(user_item)
    await db.commit()
    return True, "Mua thành công"

async def equip_item(db: AsyncSession, user_id: str, user_item_id: str):
    user_item = await db.get(models.UserItem, user_item_id)
    if not user_item or user_item.user_id != user_id:
        return False, "Vật phẩm không tồn tại hoặc không thuộc về bạn"
        
    # We need the item_type to unequip others of same type
    item = await db.get(models.ShopItem, user_item.item_id)
    
    if user_item.is_equipped:
        # Just unequip
        user_item.is_equipped = False
    else:
        # Unequip others of the same type
        result = await db.execute(
            select(models.UserItem)
            .join(models.ShopItem)
            .filter(models.UserItem.user_id == user_id, models.ShopItem.item_type == item.item_type)
        )
        for ui in result.scalars().all():
            ui.is_equipped = False
        user_item.is_equipped = True
        
    await db.commit()
    return True, "Cập nhật thành công"
"""

if "def get_shop_items" not in crud:
    crud += "\n" + shop_functions

with open('backend/app/crud.py', 'w', encoding='utf-8') as f:
    f.write(crud)
print("Updated crud.py")
