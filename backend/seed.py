import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine, Base, AsyncSessionLocal
from app import crud, schemas, models

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        # Tao tai khoan Admin
        admin_data = schemas.UserCreate(
            username="Admin",
            email="admin@zsmrecord.com",
            password="adminpassword"
        )
        admin_user = await crud.create_user(db, admin_data)
        admin_user.role = models.RoleEnum.ADMIN
        await db.commit()
        print(f"[OK] Tai khoan Admin da tao: username=Admin | password=adminpassword")
        print("[OK] Co so du lieu da khoi tao thanh cong (khong co du lieu mau).")

if __name__ == "__main__":
    asyncio.run(init_db())
