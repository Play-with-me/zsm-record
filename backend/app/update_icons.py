import asyncio
import json
from .database import AsyncSessionLocal
from .models import ShopItem
from sqlalchemy.future import select

# Mappings
# Name color: just color value
# Badge: url to iconify or flaticon
# Frame: css string or url to frame

async def update():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ShopItem))
        items = result.scalars().all()
        for item in items:
            meta = item.metadata_value
            if item.item_type == 'name_color':
                icon = f"https://api.iconify.design/mdi/format-color-text.svg?color={meta.replace('#', '%23')}"
                item.metadata_value = json.dumps({"value": meta, "icon": icon})
            elif item.item_type == 'badge':
                # Map emojis to iconify URLs
                if meta == '🔰': icon = 'https://api.iconify.design/mdi/shield-star.svg?color=%23808080'
                elif meta == '💪': icon = 'https://api.iconify.design/mdi/arm-flex.svg?color=%23808080'
                elif meta == '🌿': icon = 'https://api.iconify.design/mdi/leaf.svg?color=%23808080'
                elif meta == '💧': icon = 'https://api.iconify.design/mdi/water.svg?color=%231E90FF'
                elif meta == '🐬': icon = 'https://api.iconify.design/mdi/dolphin.svg?color=%231E90FF'
                elif meta == '❄️': icon = 'https://api.iconify.design/mdi/snowflake.svg?color=%2300FFFF'
                elif meta == '🧪': icon = 'https://api.iconify.design/mdi/flask.svg?color=%23800080'
                elif meta == '👾': icon = 'https://api.iconify.design/mdi/alien.svg?color=%23800080'
                elif meta == '♾️': icon = 'https://api.iconify.design/mdi/infinity.svg?color=%23800080'
                elif meta == '🏆': icon = 'https://api.iconify.design/mdi/trophy.svg?color=%23FFD700'
                elif meta == '⭐': icon = 'https://api.iconify.design/mdi/star.svg?color=%23FFD700'
                elif meta == '⚡': icon = 'https://api.iconify.design/mdi/lightning-bolt.svg?color=%23FFD700'
                elif meta == '👹': icon = 'https://api.iconify.design/mdi/ghost.svg?color=%23FF0000'
                elif meta == '☢️': icon = 'https://api.iconify.design/mdi/radioactive.svg?color=%23FF0000'
                elif meta == '❤️‍🔥': icon = 'https://api.iconify.design/mdi/heart-flash.svg?color=%23FF0000'
                else: icon = 'https://api.iconify.design/mdi/star-circle.svg?color=%23ffffff'
                item.metadata_value = json.dumps({"value": meta, "icon": icon})
            elif item.item_type == 'avatar_frame':
                # Replace fake imgur links with valid CSS box-shadows and iconify icons
                if "imgur" in meta:
                    color = "#ffffff"
                    if "Xám" in item.name: color = "#808080"
                    if "Xanh Dương" in item.name: color = "#1E90FF"
                    if "Tím" in item.name: color = "#8A2BE2"
                    if "Vàng" in item.name: color = "#FFD700"
                    if "Đỏ" in item.name: color = "#FF0000"
                    
                    val = f"0 0 10px {color}, inset 0 0 10px {color}"
                    if "Gỗ" in item.name: val = "0 0 5px #8B4513"
                    if "Rồng" in item.name: val = "0 0 15px #FFD700"
                    icon = f"https://api.iconify.design/mdi/account-circle-outline.svg?color={color.replace('#', '%23')}"
                    item.metadata_value = json.dumps({"value": val, "icon": icon})
        
        await session.commit()
        print("Updated items!")

if __name__ == "__main__":
    asyncio.run(update())
