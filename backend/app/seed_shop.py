import asyncio
from sqlalchemy.future import select
from .database import engine, AsyncSessionLocal
from .models import ShopItem
from uuid import uuid4

SHOP_ITEMS = [
    # Common (Xám) - 100-300
    {"name": "[Xám] Tên Xám Khói", "desc": "Màu tên xám khói giản dị", "price": 100, "type": "name_color", "meta": "#808080"},
    {"name": "[Xám] Tên Tro Tàn", "desc": "Màu tên tro tàn", "price": 150, "type": "name_color", "meta": "#A9A9A9"},
    {"name": "[Xám] Khung Gỗ", "desc": "Khung avatar gỗ đơn giản", "price": 200, "type": "avatar_frame", "meta": "https://i.imgur.com/kS9lY4v.png"},
    {"name": "[Xám] Khung Đá", "desc": "Khung avatar đá tảng", "price": 250, "type": "avatar_frame", "meta": "https://i.imgur.com/j4cZb6w.png"},
    {"name": "[Xám] Khung Sắt", "desc": "Khung avatar bằng sắt thép", "price": 300, "type": "avatar_frame", "meta": "https://i.imgur.com/3Yp4aVn.png"},
    {"name": "[Xám] Huy Hiệu Tân Binh", "desc": "Chứng nhận tân binh", "price": 100, "type": "badge", "meta": "🔰"},
    {"name": "[Xám] Huy Hiệu Nỗ Lực", "desc": "Cố gắng từng ngày", "price": 200, "type": "badge", "meta": "💪"},
    {"name": "[Xám] Huy Hiệu Cỏ Dại", "desc": "Sức sống mãnh liệt", "price": 150, "type": "badge", "meta": "🌿"},
    {"name": "[Xám] Tên Bạc Sỉu", "desc": "Màu nâu nhạt của bạc sỉu", "price": 250, "type": "name_color", "meta": "#B59D88"},
    {"name": "[Xám] Khung Rỉ Sét", "desc": "Khung sắt đã rỉ", "price": 100, "type": "avatar_frame", "meta": "https://i.imgur.com/P5e5z1S.png"},

    # Rare (Xanh Dương) - 500-1000
    {"name": "[Xanh Dương] Tên Biển Xanh", "desc": "Màu xanh của đại dương sâu thẳm", "price": 500, "type": "name_color", "meta": "#1E90FF"},
    {"name": "[Xanh Dương] Tên Lam Ngọc", "desc": "Màu xanh ngọc bích quý giá", "price": 700, "type": "name_color", "meta": "#00CED1"},
    {"name": "[Xanh Dương] Tên Băng Giá", "desc": "Màu xanh lạnh lẽo của băng", "price": 800, "type": "name_color", "meta": "#00FFFF"},
    {"name": "[Xanh Dương] Khung Đại Dương", "desc": "Khung avatar vệt nước biển", "price": 900, "type": "avatar_frame", "meta": "https://i.imgur.com/2Xy5f3T.png"},
    {"name": "[Xanh Dương] Khung Băng Tuyết", "desc": "Khung bông tuyết rơi", "price": 1000, "type": "avatar_frame", "meta": "https://i.imgur.com/J7t6j8Q.png"},
    {"name": "[Xanh Dương] Khung Mây Trời", "desc": "Khung mây bồng bềnh", "price": 850, "type": "avatar_frame", "meta": "https://i.imgur.com/uR1R3v9.png"},
    {"name": "[Xanh Dương] Huy Hiệu Nước", "desc": "Nguyên tố nước", "price": 600, "type": "badge", "meta": "💧"},
    {"name": "[Xanh Dương] Huy Hiệu Cá Heo", "desc": "Sự linh hoạt trên đường đua", "price": 750, "type": "badge", "meta": "🐬"},
    {"name": "[Xanh Dương] Huy Hiệu Băng Gió", "desc": "Lạnh như băng, nhanh như gió", "price": 950, "type": "badge", "meta": "❄️"},
    {"name": "[Xanh Dương] Tên Bầu Trời", "desc": "Màu xanh hi vọng", "price": 650, "type": "name_color", "meta": "#87CEEB"},

    # Epic (Tím) - 1500-3000
    {"name": "[Tím] Tên Tím Than", "desc": "Màu tím huyền bí", "price": 1500, "type": "name_color", "meta": "#800080"},
    {"name": "[Tím] Tên Neon Nóng", "desc": "Màu hồng tím neon rực rỡ", "price": 2000, "type": "name_color", "meta": "#FF00FF"},
    {"name": "[Tím] Tên Ánh Sao Tím", "desc": "Bầu trời đêm huyền ảo", "price": 2500, "type": "name_color", "meta": "#8A2BE2"},
    {"name": "[Tím] Khung Ma Thuật", "desc": "Khung phép thuật toả sáng", "price": 2800, "type": "avatar_frame", "meta": "https://i.imgur.com/1B5N8c7.png"},
    {"name": "[Tím] Khung Không Gian", "desc": "Khung vũ trụ bao la", "price": 3000, "type": "avatar_frame", "meta": "https://i.imgur.com/4J9Y7h2.png"},
    {"name": "[Tím] Khung Tinh Vân", "desc": "Đám mây sao đầy màu sắc", "price": 2700, "type": "avatar_frame", "meta": "https://i.imgur.com/7b8w3h1.png"},
    {"name": "[Tím] Huy Hiệu Độc Dược", "desc": "Kẻ thống trị bóng tối", "price": 1800, "type": "badge", "meta": "🧪"},
    {"name": "[Tím] Huy Hiệu Ma Quái", "desc": "Khó lường và bí ẩn", "price": 2200, "type": "badge", "meta": "👾"},
    {"name": "[Tím] Huy Hiệu Vô Cực", "desc": "Không có giới hạn", "price": 2900, "type": "badge", "meta": "♾️"},
    {"name": "[Tím] Tên Thạch Anh", "desc": "Đá thạch anh tím", "price": 1700, "type": "name_color", "meta": "#9370DB"},

    # Legendary (Vàng) - 5000-10000
    {"name": "[Vàng] Tên Hoàng Kim", "desc": "Màu vàng hoàng gia chói lọi", "price": 5000, "type": "name_color", "meta": "#FFD700"},
    {"name": "[Vàng] Tên Ánh Sáng", "desc": "Toả sáng rực rỡ mọi góc nhìn", "price": 7000, "type": "name_color", "meta": "#FFFF00"},
    {"name": "[Vàng] Tên Lôi Thần", "desc": "Sức mạnh của tia chớp", "price": 8500, "type": "name_color", "meta": "#FF8C00"},
    {"name": "[Vàng] Khung Vương Miện", "desc": "Khung dành cho nhà vua", "price": 9500, "type": "avatar_frame", "meta": "https://i.imgur.com/9v8B2v2.png"},
    {"name": "[Vàng] Khung Rồng Vàng", "desc": "Song long chầu nguyệt", "price": 10000, "type": "avatar_frame", "meta": "https://i.imgur.com/8N4M3v3.png"},
    {"name": "[Vàng] Khung Hào Quang", "desc": "Ánh hào quang rực rỡ", "price": 8000, "type": "avatar_frame", "meta": "https://i.imgur.com/3V2X8Z4.png"},
    {"name": "[Vàng] Huy Hiệu Quán Quân", "desc": "Kẻ mạnh nhất", "price": 6000, "type": "badge", "meta": "🏆"},
    {"name": "[Vàng] Huy Hiệu Ngôi Sao", "desc": "Siêu sao đường đua", "price": 7500, "type": "badge", "meta": "⭐"},
    {"name": "[Vàng] Huy Hiệu Sấm Sét", "desc": "Tốc độ ánh sáng", "price": 9000, "type": "badge", "meta": "⚡"},
    {"name": "[Vàng] Tên Nhật Bình", "desc": "Mặt trời chói chang", "price": 6500, "type": "name_color", "meta": "#F0E68C"},

    # Mythic (Đỏ) - 20000-50000
    {"name": "[Đỏ] Tên Máu Lửa", "desc": "Màu đỏ rực của máu và lửa", "price": 20000, "type": "name_color", "meta": "#FF0000"},
    {"name": "[Đỏ] Tên Dung Nham", "desc": "Nóng bỏng thiêu rụi mọi thứ", "price": 25000, "type": "name_color", "meta": "#FF4500"},
    {"name": "[Đỏ] Tên Quỷ Dữ", "desc": "Đỏ sậm của địa ngục", "price": 30000, "type": "name_color", "meta": "#8B0000"},
    {"name": "[Đỏ] Khung Phượng Hoàng", "desc": "Phượng hoàng niết bàn", "price": 40000, "type": "avatar_frame", "meta": "https://i.imgur.com/1C7V5M6.png"},
    {"name": "[Đỏ] Khung Hỏa Địa Ngục", "desc": "Ngọn lửa không bao giờ tắt", "price": 45000, "type": "avatar_frame", "meta": "https://i.imgur.com/2D8W6N7.png"},
    {"name": "[Đỏ] Khung Huyết Nguyệt", "desc": "Mặt trăng máu", "price": 50000, "type": "avatar_frame", "meta": "https://i.imgur.com/4F9X7P8.png"},
    {"name": "[Đỏ] Huy Hiệu Ác Quỷ", "desc": "Chúa tể bóng tối", "price": 35000, "type": "badge", "meta": "👹"},
    {"name": "[Đỏ] Huy Hiệu Cảnh Báo", "desc": "Nguy hiểm tột độ", "price": 38000, "type": "badge", "meta": "☢️"},
    {"name": "[Đỏ] Huy Hiệu Trái Tim Đỏ", "desc": "Tình yêu mãnh liệt với tốc độ", "price": 28000, "type": "badge", "meta": "❤️‍🔥"},
    {"name": "[Đỏ] Tên Hồng Ngọc", "desc": "Đá Ruby quý hiếm nhất", "price": 32000, "type": "name_color", "meta": "#DC143C"},
]

async def seed_shop():
    async with AsyncSessionLocal() as session:
        # Check if shop has items
        result = await session.execute(select(ShopItem).limit(1))
        first = result.scalars().first()
        if not first:
            print("[OK] Seeding 50 shop items...")
            for item in SHOP_ITEMS:
                new_item = ShopItem(
                    id=uuid4().hex,
                    name=item["name"],
                    description=item["desc"],
                    price=item["price"],
                    item_type=item["type"],
                    metadata_value=item["meta"]
                )
                session.add(new_item)
            await session.commit()
            print("[OK] Done seeding shop items.")
        else:
            print("[OK] Shop items already exist.")
