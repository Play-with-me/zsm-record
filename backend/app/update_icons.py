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
                color = meta_val.replace('#', '%23')
                # pixel art palette
                icon = f"https://api.iconify.design/pixelarticons/paint.svg?color={color}"
                item.metadata_value = json.dumps({"value": meta_val, "icon": icon})
            elif item.item_type == 'badge':
                meta = meta_val
                # pixel art icons based on the badge meaning
                icon = 'https://api.iconify.design/pixelarticons/star.svg?color=%23FFD700'
                if meta == '🔰': icon = 'https://api.iconify.design/pixelarticons/shield.svg?color=%2332CD32'
                elif meta == '💪': icon = 'https://api.iconify.design/pixelarticons/power.svg?color=%23FF4500'
                elif meta == '🌿': icon = 'https://api.iconify.design/pixelarticons/leaf.svg?color=%23228B22'
                elif meta == '💧': icon = 'https://api.iconify.design/pixelarticons/drop.svg?color=%231E90FF'
                elif meta == '🐬': icon = 'https://api.iconify.design/pixelarticons/fish.svg?color=%2300CED1'
                elif meta == '❄️': icon = 'https://api.iconify.design/pixelarticons/snowflake.svg?color=%23ADD8E6'
                elif meta == '🧪': icon = 'https://api.iconify.design/pixelarticons/test-tube.svg?color=%239370DB'
                elif meta == '👾': icon = 'https://api.iconify.design/pixelarticons/bug.svg?color=%238A2BE2'
                elif meta == '♾️': icon = 'https://api.iconify.design/pixelarticons/infinite.svg?color=%23FF69B4'
                elif meta == '🏆': icon = 'https://api.iconify.design/pixelarticons/cup.svg?color=%23FFD700'
                elif meta == '⭐': icon = 'https://api.iconify.design/pixelarticons/star.svg?color=%23FFA500'
                elif meta == '⚡': icon = 'https://api.iconify.design/pixelarticons/zap.svg?color=%23FFFF00'
                elif meta == '👹': icon = 'https://api.iconify.design/pixelarticons/mood-sad.svg?color=%23FF0000'
                elif meta == '☢️': icon = 'https://api.iconify.design/pixelarticons/warning-box.svg?color=%237CFC00'
                elif meta == '❤️‍🔥': icon = 'https://api.iconify.design/pixelarticons/heart.svg?color=%23DC143C'
                item.metadata_value = json.dumps({"value": meta_val, "icon": icon})
            elif item.item_type == 'avatar_frame':
                color = "#ffffff"
                if "Xám" in item.name: color = "#808080"
                if "Xanh Dương" in item.name: color = "#1E90FF"
                if "Tím" in item.name: color = "#8A2BE2"
                if "Vàng" in item.name: color = "#FFD700"
                if "Đỏ" in item.name: color = "#FF0000"
                
                val = f"0 0 15px {color}, inset 0 0 10px {color}"
                if "Gỗ" in item.name: val = "0 0 5px #8B4513, inset 0 0 5px #8B4513"
                if "Rồng" in item.name: val = "0 0 20px #FF4500, inset 0 0 15px #FFD700"
                
                # Use pixelarticons box/frame for the avatar frame icon
                icon = f"https://api.iconify.design/pixelarticons/checkbox.svg?color={color.replace('#', '%23')}"
                if "Rồng" in item.name: icon = "https://api.iconify.design/pixelarticons/fire.svg?color=%23FF4500"
                
                item.metadata_value = json.dumps({"value": val, "icon": icon})
        
        await session.commit()
        print("Updated icons beautifully!")

if __name__ == "__main__":
    asyncio.run(update())
