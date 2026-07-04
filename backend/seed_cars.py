import asyncio
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.models import Car

async def seed_cars():
    filepath = os.path.join(os.path.dirname(__file__), "cars_list.txt")
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    cars_data = []
    current_class = "A"
    
    for line in lines:
        line = line.strip()
        # Clean up bullet points if any
        if line.startswith("•\t") or line.startswith("• "):
            line = line[2:].strip()
            
        if not line:
            continue
            
        if line.lower() == "xe a":
            current_class = "A"
            continue
        elif line.lower() == "xe t":
            current_class = "T"
            continue
            
        cars_data.append({"name": line, "car_class": current_class})

    async with AsyncSessionLocal() as db:
        added_count = 0
        for data in cars_data:
            name = data["name"]
            c_class = data["car_class"]
            
            # Check if exists
            result = await db.execute(select(Car).filter(Car.name == name))
            existing_car = result.scalars().first()
            
            if not existing_car:
                new_car = Car(name=name, car_class=c_class)
                db.add(new_car)
                added_count += 1
                
                await db.commit()
        print(f"[OK] Da kiem tra va them cac xe vao co so du lieu.")
