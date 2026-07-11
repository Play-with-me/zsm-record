from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/record-board", tags=["record-board"])

@router.get("", response_model=List[schemas.RecordBoardEntry])
async def read_record_board(
    map_id: Optional[str] = None, 
    car_id: Optional[str] = None,
    pet_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    # This will return the top records dynamically based on filters
    return await crud.get_record_board(db, map_id=map_id, car_id=car_id, pet_id=pet_id)

@router.get("/by-map", response_model=List[schemas.MapLeaderboardEntry])
async def read_record_board_by_map(
    map_id: Optional[str] = None, 
    car_id: Optional[str] = None,
    pet_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Return leaderboard grouped by map, ranked by lowest record time"""
    return await crud.get_record_board_by_map(db, map_id=map_id, car_id=car_id, pet_id=pet_id)

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
