import re

with open('backend/app/schemas.py', 'r', encoding='utf-8') as f:
    text = f.read()

shop_block = """
# ----------------- Shop -----------------
class ShopItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: int = 0
    item_type: str
    metadata_value: str

class ShopItemCreate(ShopItemBase):
    pass

class ShopItemResponse(ShopItemBase):
    id: str
    class Config:
        from_attributes = True

class UserItemResponse(BaseModel):
    id: str
    user_id: str
    item_id: str
    is_equipped: bool
    purchased_at: datetime
    item: ShopItemResponse
    class Config:
        from_attributes = True
"""

# Remove the shop block from the end
text = text.replace(shop_block, "")

# Insert shop block before Auth
auth_index = text.find("# ----------------- Auth -----------------")
text = text[:auth_index] + shop_block + "\n" + text[auth_index:]

# Add equipped_items to UserResponse
text = text.replace(
    "avatar_update_count: int = 0\n    # items will be added via separate endpoint or updated later",
    "avatar_update_count: int = 0\n    items: List[UserItemResponse] = []"
)

with open('backend/app/schemas.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("done")
