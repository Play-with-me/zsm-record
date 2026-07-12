with open('app/routers/board.py', 'a', encoding='utf-8') as f:
    f.write('''
@router.get("/tournaments/active")
async def get_active_tournaments(db: AsyncSession = Depends(get_db)):
    from sqlalchemy.future import select
    from .. import models
    import datetime
    now = datetime.datetime.utcnow()
    result = await db.execute(
        select(models.Tournament)
        .filter(models.Tournament.is_active == True)
        .filter(models.Tournament.start_time <= now)
        .filter(models.Tournament.end_time >= now)
    )
    t = result.scalars().first()
    if t:
        return {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "map_id": t.map_id,
            "start_time": t.start_time,
            "end_time": t.end_time
        }
    return None
''')
print('Appended tournament to board.py')
