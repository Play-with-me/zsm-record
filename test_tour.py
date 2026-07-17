import asyncio
from backend.app.database import engine, Base, AsyncSessionLocal
from backend.app import models
from backend.app.schemas import TournamentCreate

async def main():
    async with AsyncSessionLocal() as db:
        t = TournamentCreate(name='Test 2', description='abc', participants=['user1'])
        new_t = models.Tournament(
            name=t.name,
            description=t.description,
            map_id=t.map_id,
            start_time=t.start_time,
            end_time=t.end_time,
            is_active=t.is_active,
            format=t.format,
            status=models.TournamentStatusEnum.ONGOING if len(t.participants) > 1 else models.TournamentStatusEnum.DRAFT
        )
        db.add(new_t)
        await db.commit()
        await db.refresh(new_t)
        print('Created tournament:', new_t.id)

asyncio.run(main())
