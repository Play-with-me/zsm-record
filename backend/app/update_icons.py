import asyncio
import json
from .database import AsyncSessionLocal
from .models import ShopItem
from sqlalchemy.future import select

try:
    from .icons_data import ICONS
except ImportError:
    ICONS = {}

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
                meta = meta_val
                # default pixel art icons
                icon = 'https://api.iconify.design/pixelarticons/star.svg?color=%23FFD700'
            elif item.item_type == 'avatar_frame':
                color = "#ffffff"
                val = f"0 0 15px {color}, inset 0 0 10px {color}"
                icon = f"https://api.iconify.design/pixelarticons/checkbox.svg?color={color.replace('#', '%23')}"
                
            # If we generated a custom pollinations AI icon, use it!
            if item.name in ICONS:
                icon = ICONS[item.name]
                
            if icon:
                # Retain the previous value logic or assign what we found
                if item.item_type == 'avatar_frame':
                    pass # Val logic above was a fallback, let's keep original meta_val
                item.metadata_value = json.dumps({"value": meta_val, "icon": icon})
        
        await session.commit()
        print("Updated icons beautifully!")

if __name__ == "__main__":
    asyncio.run(update())
