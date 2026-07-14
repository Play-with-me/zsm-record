import asyncio
import json
from backend.app.database import AsyncSessionLocal
from backend.app.models import ShopItem
from sqlalchemy.future import select

async def update():
    with open("pollinations_icons.json", "r", encoding="utf-8") as f:
        icons = json.load(f)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ShopItem))
        items = result.scalars().all()
        
        for item in items:
            try:
                meta_json = json.loads(item.metadata_value)
                meta_val = meta_json.get("value", "")
            except:
                meta_val = item.metadata_value

            if item.name in icons:
                # Update icon with the generated one
                meta_json = json.loads(item.metadata_value) if "{" in item.metadata_value else {"value": item.metadata_value}
                meta_json["icon"] = icons[item.name]
                item.metadata_value = json.dumps(meta_json)
        
        await session.commit()
        print("Updated database items with pollinations.ai base64 images successfully!")

if __name__ == "__main__":
    asyncio.run(update())
