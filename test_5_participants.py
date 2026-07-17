import asyncio
from backend.app.database import engine, Base, AsyncSessionLocal
from backend.app import models
from backend.app.schemas import TournamentCreate
from backend.app.routers.board import create_tournament

class MockUser:
    role = models.RoleEnum.ADMIN

async def main():
    async with AsyncSessionLocal() as db:
        users = [models.User(username=f'u_{i}', email=f'u_{i}@t.com', password_hash='xx', role=models.RoleEnum.USER) for i in range(5)]
        db.add_all(users)
        await db.commit()
        for u in users:
            await db.refresh(u)
        
        t = TournamentCreate(name='Test 5 Participants', description='abc', participants=[u.id for u in users])
        try:
            res = await create_tournament(t, db, MockUser())
            print('SUCCESS:', res.id)
        except Exception as e:
            print('ERROR TYPE:', type(e))
            print('ERROR:', e)
            import traceback
            traceback.print_exc()

asyncio.run(main())
