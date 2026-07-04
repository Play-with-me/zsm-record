import asyncio
import os
from sqlalchemy import text
from database import SessionLocal
from models import Car

async def fix_cars():
    db = SessionLocal()
    try:
        print("[INFO] Dang xoa toan bo xe cu de sua loi...")
        # Wipe the table completely
        db.query(Car).delete()
        db.commit()

        file_path = os.path.join(os.path.dirname(__file__), 'cars_list.txt')
        if not os.path.exists(file_path):
            print("[WARN] Khong tim thay cars_list.txt")
            return

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
            
        current_class = "A"
        added_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("•\t") or line.startswith("• "):
                line = line[2:].strip()
                
            if line.lower() == "xe a":
                current_class = "A"
                continue
            elif line.lower() == "xe t":
                current_class = "T"
                continue
                
            name = line
            new_car = Car(name=name, car_class=current_class)
            db.add(new_car)
            added_count += 1
                
        db.commit()
        print(f"[OK] Da them lai {added_count} xe moi vao co so du lieu thanh cong.")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] fix_cars gap loi: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(fix_cars())
