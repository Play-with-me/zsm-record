from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .routers import auth, videos, masters, board

app = FastAPI(title="ZSM Record API")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(videos.router, prefix="/api/v1")
app.include_router(masters.router, prefix="/api/v1")
app.include_router(board.router, prefix="/api/v1")

@app.on_event("startup")
async def startup():
    # Not recommended for production, but good for local dev with SQLite/simple Postgres
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Welcome to ZSM Record API"}
