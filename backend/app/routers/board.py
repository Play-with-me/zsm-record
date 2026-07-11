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

@router.get("/analytics/meta-pets")
async def get_meta_pets(db: AsyncSession = Depends(get_db)):
    from sqlalchemy.future import select
    from sqlalchemy import func
    from .. import models
    # Group by pet, count videos
    result = await db.execute(
        select(models.Pet.name, func.count(models.Video.id).label('count'))
        .join(models.Video, models.Video.pet_id == models.Pet.id)
        .filter(models.Video.visibility == "PUBLIC")
        .group_by(models.Pet.name)
        .order_by(func.count(models.Video.id).desc())
        .limit(10)
    )
    rows = result.all()
    return [{"pet": r.name, "count": r.count} for r in rows]

from fastapi import HTTPException
from pydantic import BaseModel
from datetime import datetime
from .auth import get_current_user
from .. import models

class TournamentCreate(BaseModel):
    name: str
    description: str
    map_id: str
    start_time: datetime
    end_time: datetime

@router.post("/tournaments")
async def create_tournament(
    t: TournamentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    new_t = models.Tournament(
        name=t.name,
        description=t.description,
        map_id=t.map_id,
        start_time=t.start_time,
        end_time=t.end_time,
        is_active=True
    )
    db.add(new_t)
    await db.commit()
    await db.refresh(new_t)
    return new_t

@router.get("/tournaments")
async def get_all_tournaments(db: AsyncSession = Depends(get_db)):
    from sqlalchemy.future import select
    from .. import models
    result = await db.execute(select(models.Tournament).order_by(models.Tournament.created_at.desc()))
    rows = result.scalars().all()
    return [{"id": t.id, "name": t.name, "description": t.description, "map_id": t.map_id, "start_time": t.start_time, "end_time": t.end_time, "is_active": t.is_active} for t in rows]

@router.put("/tournaments/{t_id}")
async def update_tournament(
    t_id: str,
    t: TournamentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    from sqlalchemy.future import select
    result = await db.execute(select(models.Tournament).filter(models.Tournament.id == t_id))
    t_obj = result.scalars().first()
    if not t_obj: raise HTTPException(status_code=404, detail="Tournament not found")
    
    t_obj.name = t.name
    t_obj.description = t.description
    t_obj.map_id = t.map_id
    t_obj.start_time = t.start_time
    t_obj.end_time = t.end_time
    
    await db.commit()
    await db.refresh(t_obj)
    return t_obj

@router.delete("/tournaments/{t_id}")
async def delete_tournament(
    t_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    from sqlalchemy.future import select
    result = await db.execute(select(models.Tournament).filter(models.Tournament.id == t_id))
    t_obj = result.scalars().first()
    if not t_obj: raise HTTPException(status_code=404, detail="Tournament not found")
    
    await db.delete(t_obj)
    await db.commit()
    return {"message": "Deleted tournament"}
