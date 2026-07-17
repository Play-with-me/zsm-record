import asyncio
from backend.app.database import engine, Base, AsyncSessionLocal
from backend.app import models

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as db:
        new_t = models.Tournament(
            name='Test Tournament',
            description='Test Desc',
            format=models.TournamentFormatEnum.SINGLE,
            status=models.TournamentStatusEnum.DRAFT
        )
        db.add(new_t)
        await db.commit()
        await db.refresh(new_t)
        print('Created tournament:', new_t.id)

asyncio.run(main())
