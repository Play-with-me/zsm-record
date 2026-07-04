import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import delete, text
from .database import engine, Base, AsyncSessionLocal
from .models import Car, Pet
from .routers import auth, videos, masters, board, users

app = FastAPI(title="ZSM Record API")

# Only mount local uploads folder when NOT on Cloudinary (i.e., local dev)
UPLOADS_DIR = "uploads"
if not os.getenv("CLOUDINARY_URL"):
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
        # Delete ALL cars first
        await session.execute(delete(Car))
        # Re-add from file
        for name, car_class in cars_to_add:
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
        # Delete ALL pets first
        await session.execute(delete(Pet))
        # Re-add from file
        for name in pets_to_add:
            session.add(Pet(name=name))
        await session.commit()
    print(f"[OK] Reseed pets: da them {len(pets_to_add)} pet.")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        await reseed_cars()
        await reseed_pets()
    except Exception as e:
        print(f"[WARN] reseed gap loi: {e}")

@app.get("/")
async def root():
    return {"message": "Welcome to ZSM Record API"}
