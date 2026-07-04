import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
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

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    try:
        import sys
        # Add the parent directory to sys.path if not already there, so we can import fix_cars
        parent_dir = os.path.dirname(os.path.dirname(__file__))
        if parent_dir not in sys.path:
            sys.path.append(parent_dir)
        import fix_cars
        await fix_cars.fix_cars()
        print("[OK] Chay fix_cars thanh cong.")
    except Exception as e:
        print(f"[WARN] Khong the chay fix_cars: {e}")

@app.get("/")
async def root():
    return {"message": "Welcome to ZSM Record API"}
