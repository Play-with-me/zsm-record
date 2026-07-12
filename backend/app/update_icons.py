import asyncio
import json
from .database import AsyncSessionLocal
from .models import ShopItem
from sqlalchemy.future import select

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

            if item.item_type == 'name_color':
                # Beautiful text color icon
                color = meta_val.replace('#', '%23')
                icon = f"https://api.iconify.design/noto/artist-palette.svg"
                item.metadata_value = json.dumps({"value": meta_val, "icon": icon})
            elif item.item_type == 'badge':
                # Fluent emojis / Noto emojis for badges
                meta = meta_val
                icon = 'https://api.iconify.design/noto/star.svg'
                if meta == '🔰': icon = 'https://api.iconify.design/noto/japanese-symbol-for-beginner.svg'
                elif meta == '💪': icon = 'https://api.iconify.design/noto/flexed-biceps.svg'
                elif meta == '🌿': icon = 'https://api.iconify.design/noto/herb.svg'
                elif meta == '💧': icon = 'https://api.iconify.design/noto/droplet.svg'
                elif meta == '🐬': icon = 'https://api.iconify.design/noto/dolphin.svg'
                elif meta == '❄️': icon = 'https://api.iconify.design/noto/snowflake.svg'
                elif meta == '🧪': icon = 'https://api.iconify.design/noto/test-tube.svg'
                elif meta == '👾': icon = 'https://api.iconify.design/noto/alien-monster.svg'
                elif meta == '♾️': icon = 'https://api.iconify.design/noto/infinity.svg'
                elif meta == '🏆': icon = 'https://api.iconify.design/noto/trophy.svg'
                elif meta == '⭐': icon = 'https://api.iconify.design/noto/star.svg'
                elif meta == '⚡': icon = 'https://api.iconify.design/noto/high-voltage.svg'
                elif meta == '👹': icon = 'https://api.iconify.design/noto/ogre.svg'
                elif meta == '☢️': icon = 'https://api.iconify.design/noto/radioactive.svg'
                elif meta == '❤️‍🔥': icon = 'https://api.iconify.design/noto/heart-on-fire.svg'
                item.metadata_value = json.dumps({"value": meta_val, "icon": icon})
            elif item.item_type == 'avatar_frame':
                # Avatar frame - we use a beautiful svg for the icon, and box-shadow for value
                # e.g., https://api.iconify.design/ph/frame-corners-duotone.svg
                color = "#ffffff"
                if "Xám" in item.name: color = "#808080"
                if "Xanh Dương" in item.name: color = "#1E90FF"
                if "Tím" in item.name: color = "#8A2BE2"
                if "Vàng" in item.name: color = "#FFD700"
                if "Đỏ" in item.name: color = "#FF0000"
                
                # Make the frame effect itself better
                val = f"0 0 15px {color}, inset 0 0 10px {color}"
                if "Gỗ" in item.name: val = "0 0 5px #8B4513, inset 0 0 5px #8B4513"
                if "Rồng" in item.name: val = "0 0 20px #FF4500, inset 0 0 15px #FFD700"
                
                icon = f"https://api.iconify.design/ph/circle-bold.svg?color={color.replace('#', '%23')}"
                if "Rồng" in item.name: icon = "https://api.iconify.design/noto/dragon-face.svg"
                
                item.metadata_value = json.dumps({"value": val, "icon": icon})
        
        await session.commit()
        print("Updated icons beautifully!")

if __name__ == "__main__":
    asyncio.run(update())
