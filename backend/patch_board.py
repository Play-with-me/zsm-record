with open('app/routers/board.py', 'a', encoding='utf-8') as f:
    f.write('''
@router.get("/analytics/meta")
async def get_meta_analytics(db: AsyncSession = Depends(get_db)):
    from sqlalchemy.future import select
    from sqlalchemy import func
    from .. import models
    # Group by car, count videos
    result = await db.execute(
        select(models.Car.name, func.count(models.Video.id).label('count'))
        .join(models.Video, models.Video.car_id == models.Car.id)
        .filter(models.Video.visibility == "PUBLIC")
        .group_by(models.Car.name)
        .order_by(func.count(models.Video.id).desc())
        .limit(10)
    )
    rows = result.all()
    return [{"car": r.name, "count": r.count} for r in rows]
''')
print('Appended analytics to board.py')
