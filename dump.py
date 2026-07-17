import asyncio
from backend.app.database import async_session_maker
from backend.app.models import TournamentMatch
from sqlalchemy.future import select

async def main():
    async with async_session_maker() as db:
        res = await db.execute(select(TournamentMatch).filter(TournamentMatch.tournament_id == 'c84029a4-4c27-4180-8fc8-c30813aea4c0'))
        matches = res.scalars().all()
        for m in matches:
            print(f'R: {m.round_sequence}, I: {m.match_index}, P1: {m.player1_id}, P2: {m.player2_id}')
asyncio.run(main())
