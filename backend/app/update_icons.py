import asyncio
import json
from .database import AsyncSessionLocal
from .models import ShopItem
from sqlalchemy.future import select

try:
    from .icons_data import ICONS
except ImportError:
    ICONS = {}

# Map generic names to DB item name keywords
MAPPINGS = {
    "Khung Gỗ": ["gỗ", "thư sinh", "đơn giản", "xám"],
    "Khung Bạc": ["bạc", "đá", "sắt"],
    "Khung Vàng": ["vàng", "vương giả", "hoàng kim", "vương miện", "quán quân"],
    "Khung Kim Cương": ["kim cương", "băng", "đại dương", "xanh dương"],
    "Khung Lửa Đỏ": ["lửa", "phượng hoàng", "đỏ", "dung nham"],
    "Khung Hắc Ám": ["hắc ám", "ma thuật", "tím", "tinh vân"],
    "Huy Hiệu Tập Sự": ["tân binh", "cỏ", "nỗ lực", "tập sự"],
    "Huy Hiệu Cao Thủ": ["cá heo", "nước", "cao thủ"],
    "Huy Hiệu Tốc Độ": ["sấm sét", "tốc độ", "sao", "ngôi sao"],
    "Huy Hiệu Huyền Thoại": ["vô cực", "độc dược", "huyền thoại"],
    "Huy Hiệu Rồng Lửa": ["rồng", "quỷ", "trái tim"],
    "Huy Hiệu Hắc Ám": ["ác quỷ", "cảnh báo", "ma quái"]
}

async def update():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ShopItem))
        items = result.scalars().all()
        for item in items:
            try:
                meta_json = json.loads(item.metadata_value)
                meta_val = meta_json.get("value", "")
            except:
                meta_val = item.metadata_value
            
            icon = None
            if item.item_type == 'name_color':
                color = meta_val.replace('#', '%23')
                # pixel art palette
                icon = f"https://api.iconify.design/pixelarticons/paint.svg?color={color}"
            elif item.item_type == 'badge':
                icon = 'https://api.iconify.design/pixelarticons/star.svg?color=%23FFD700'
            elif item.item_type == 'avatar_frame':
                color = "#ffffff"
                icon = f"https://api.iconify.design/pixelarticons/checkbox.svg?color={color.replace('#', '%23')}"
                
            name_lower = item.name.lower()
            
            # Find matching custom icon based on mappings
            for custom_name, keywords in MAPPINGS.items():
                if any(kw in name_lower for kw in keywords):
                    if (item.item_type == 'avatar_frame' and 'Khung' in custom_name) or (item.item_type == 'badge' and 'Huy Hiệu' in custom_name):
                        if custom_name in ICONS:
                            icon = ICONS[custom_name]
                            break

            if icon:
                # If we have a custom generated icon, it will be the base64 string
                item.metadata_value = json.dumps({"value": meta_val, "icon": icon})
        
        await session.commit()
        print("Updated icons beautifully!")

if __name__ == "__main__":
    asyncio.run(update())
