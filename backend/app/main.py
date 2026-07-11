import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import delete, text
from .database import engine, Base, AsyncSessionLocal
from .models import Car, Pet, Map
from .routers import auth, videos, masters, board, users

app = FastAPI(title="ZSM Record API")

# Always mount local uploads folder for fallback (even if Cloudinary is used)
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(videos.router, prefix="/api/v1")
app.include_router(masters.router, prefix="/api/v1")
app.include_router(board.router, prefix="/api/v1")

async def reseed_cars():
    """Wipe and re-seed cars table from cars_list.txt."""
    cars_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cars_list.txt')
    if not os.path.exists(cars_file):
        print("[WARN] Khong tim thay cars_list.txt, bo qua reseed.")
        return

    with open(cars_file, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    current_class = "A"
    cars_to_add = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        # Strip bullet characters
        if line.startswith('\u2022') or line.startswith('\u00b7'):
            line = line[1:].strip()
        line_lower = line.lower()
        # Detect category headers - skip them, just switch class
        if line_lower.startswith("xe a") and len(line_lower) <= 6:
            current_class = "A"
            continue
        elif line_lower.startswith("xe t") and len(line_lower) <= 6:
            current_class = "T"
            continue
        name = line.strip()
        if name:
            cars_to_add.append((name, current_class))

    async with AsyncSessionLocal() as session:
        from sqlalchemy.future import select
        
        # Upsert Cars
        result = await session.execute(select(Car))
        existing_cars = {c.name: c for c in result.scalars().all()}
        
        for name, car_class in cars_to_add:
            if name in existing_cars:
                existing_cars[name].car_class = car_class
            else:
                session.add(Car(name=name, car_class=car_class))
                
        await session.commit()
    print(f"[OK] Reseed cars: da them {len(cars_to_add)} xe (A/T phan loai chinh xac).")

async def reseed_pets():
    """Wipe and re-seed pets table from pets_list.txt."""
    pets_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pets_list.txt')
    if not os.path.exists(pets_file):
        print("[WARN] Khong tim thay pets_list.txt, bo qua reseed.")
        return

    with open(pets_file, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    pets_to_add = []
    seen = set()
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        # Strip bullet characters
        if line.startswith('\u2022') or line.startswith('\u00b7'):
            line = line[1:].strip()
        name = line.strip()
        if name and name not in seen:
            pets_to_add.append(name)
            seen.add(name)

    async with AsyncSessionLocal() as session:
        from sqlalchemy.future import select
        
        # Upsert Pets
        result = await session.execute(select(Pet))
        existing_pets = {p.name: p for p in result.scalars().all()}
        
        for name in pets_to_add:
            if name not in existing_pets:
                session.add(Pet(name=name))
                
        await session.commit()
    print(f"[OK] Reseed pets: da them {len(pets_to_add)} pet.")

async def reseed_maps():
    """Wipe and re-seed maps table from maps_list.txt."""
    maps_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'maps_list.txt')
    if not os.path.exists(maps_file):
        print("[WARN] Khong tim thay maps_list.txt, bo qua reseed.")
        return

    with open(maps_file, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    current_difficulty = 1
    maps_to_add = []
    seen = set()
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        
        # Check for difficulty headers (e.g. "1 sao:", "2 sao:")
        if line.lower().endswith("sao:"):
            try:
                current_difficulty = int(line.split()[0])
            except:
                pass
            continue

        # Strip bullet characters
        if line.startswith('\u2022') or line.startswith('\u00b7'):
            line = line[1:].strip()
        name = line.strip()
        
        if name and name not in seen:
            maps_to_add.append((name, current_difficulty))
            seen.add(name)

    async with AsyncSessionLocal() as session:
        from .models import Map
        from sqlalchemy.future import select
        
        # Get existing maps
        result = await session.execute(select(Map))
        existing_maps = {m.name: m for m in result.scalars().all()}
        
        # Upsert maps
        for name, diff in maps_to_add:
            if name in existing_maps:
                existing_maps[name].difficulty = diff
            else:
                session.add(Map(name=name, difficulty=diff))
                
        await session.commit()
    print(f"[OK] Reseed maps: da them {len(maps_to_add)} map voi do kho (sao).")



@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE maps ADD COLUMN difficulty INTEGER DEFAULT 1"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN avatar_update_count INTEGER DEFAULT 0"))
    except Exception:
        pass

    try:
        async with engine.begin() as conn:
            await conn.execute(text("ALTER TABLE users ADD COLUMN exp INTEGER DEFAULT 0"))
    except Exception:
        pass

    try:
        await reseed_maps()
        await reseed_cars()
        await reseed_pets()
    except Exception as e:
        print(f"[WARN] reseed gap loi: {e}")

@app.get("/")
async def root():
    return {"message": "Welcome to ZSM Record API"}
