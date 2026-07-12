with open('app/routers/board.py', 'a', encoding='utf-8') as f:
    f.write('''
@router.get("/tournaments")
async def get_all_tournaments(db: AsyncSession = Depends(get_db)):
    from sqlalchemy.future import select
    from .. import models
    result = await db.execute(select(models.Tournament).order_by(models.Tournament.created_at.desc()))
    rows = result.scalars().all()
    return [{"id": t.id, "name": t.name, "description": t.description, "map_id": t.map_id, "start_time": t.start_time, "end_time": t.end_time, "is_active": t.is_active} for t in rows]
''')
print('Appended GET /tournaments to board.py')
