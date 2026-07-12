import sqlite3
import uuid

def seed():
    conn = sqlite3.connect('backend/zsm_record.db')
    c = conn.cursor()
    
    # Create tables if not exist (UserItem, ShopItem)
    c.execute('''
    CREATE TABLE IF NOT EXISTS shop_items (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL DEFAULT 0,
        item_type TEXT NOT NULL,
        metadata_value TEXT NOT NULL
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS user_items (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        item_id TEXT NOT NULL,
        is_equipped BOOLEAN DEFAULT 0,
        purchased_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(item_id) REFERENCES shop_items(id) ON DELETE CASCADE
    )
    ''')
    
    # Check if already seeded
    c.execute('SELECT COUNT(*) FROM shop_items')
    if c.fetchone()[0] > 0:
        print("Already seeded")
        return
        
    shop_items = [
        (str(uuid.uuid4()), "Màu Tên Đỏ Chói", "Nổi bật giữa đám đông", 50, "name_color", "#FF3333"),
        (str(uuid.uuid4()), "Màu Tên Hoàng Kim", "Sắc vàng của người chiến thắng", 100, "name_color", "#FFD700"),
        (str(uuid.uuid4()), "Màu Tên Xanh Neon", "Phong cách Cyberpunk", 150, "name_color", "#00FFCC"),
        (str(uuid.uuid4()), "Viền Bạc Thư Sinh", "Khung viền nhẹ nhàng", 200, "avatar_frame", "2px solid #C0C0C0"),
        (str(uuid.uuid4()), "Viền Vàng Vương Giả", "Khung viền sang trọng rực rỡ", 500, "avatar_frame", "2px solid #FFD700; box-shadow: 0 0 10px #FFD700;"),
        (str(uuid.uuid4()), "Viền Tím Vô Cực", "Sức mạnh tối thượng", 800, "avatar_frame", "3px solid #9933FF; box-shadow: 0 0 15px #9933FF;")
    ]
    
    c.executemany('INSERT INTO shop_items (id, name, description, price, item_type, metadata_value) VALUES (?,?,?,?,?,?)', shop_items)
    conn.commit()
    conn.close()
    print("Seeded shop items successfully!")

if __name__ == "__main__":
    seed()
