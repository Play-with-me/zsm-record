import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import engine, AsyncSessionLocal
from backend.app import models

async def seed():
    async with AsyncSessionLocal() as db:
        # Create tables if not exist (UserItem, ShopItem)
        async with engine.begin() as conn:
            await conn.run_sync(models.Base.metadata.create_all)
            
        # Check if already seeded
        from sqlalchemy import select
        result = await db.execute(select(models.ShopItem))
        items = result.scalars().all()
        if items:
            print("Already seeded")
            return
            
        shop_items = [
            models.ShopItem(name="Màu Tên Đỏ Chói", description="Nổi bật giữa đám đông", price=50, item_type="name_color", metadata_value="#FF3333"),
            models.ShopItem(name="Màu Tên Hoàng Kim", description="Sắc vàng của người chiến thắng", price=100, item_type="name_color", metadata_value="#FFD700"),
            models.ShopItem(name="Màu Tên Xanh Neon", description="Phong cách Cyberpunk", price=150, item_type="name_color", metadata_value="#00FFCC"),
            models.ShopItem(name="Viền Bạc Thư Sinh", description="Khung viền nhẹ nhàng", price=200, item_type="avatar_frame", metadata_value="2px solid #C0C0C0"),
            models.ShopItem(name="Viền Vàng Vương Giả", description="Khung viền sang trọng rực rỡ", price=500, item_type="avatar_frame", metadata_value="2px solid #FFD700; box-shadow: 0 0 10px #FFD700;"),
            models.ShopItem(name="Viền Tím Vô Cực", description="Sức mạnh tối thượng", price=800, item_type="avatar_frame", metadata_value="3px solid #9933FF; box-shadow: 0 0 15px #9933FF;")
        ]
        db.add_all(shop_items)
        await db.commit()
        print("Seeded shop items successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
