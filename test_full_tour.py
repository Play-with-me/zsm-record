import asyncio
from backend.app.database import engine, Base, AsyncSessionLocal
from backend.app import models
from backend.app.schemas import TournamentCreate
from backend.app.routers.board import create_tournament

# Mock current user
class MockUser:
    role = models.RoleEnum.ADMIN

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as db:
        # Create some dummy users
        u1 = models.User(username='u1', email='u1@t.com', password_hash='xx', role=models.RoleEnum.USER)
        u2 = models.User(username='u2', email='u2@t.com', password_hash='xx', role=models.RoleEnum.USER)
        db.add_all([u1, u2])
        await db.commit()
        await db.refresh(u1)
        await db.refresh(u2)
        
        t = TournamentCreate(name='Test Full API', description='abc', participants=[u1.id, u2.id])
        try:
            res = await create_tournament(t, db, MockUser())
            print('SUCCESS:', res.id)
        except Exception as e:
            print('ERROR:', e)
            import traceback
            traceback.print_exc()

asyncio.run(main())
