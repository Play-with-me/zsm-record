with open('app/routers/board.py', 'a', encoding='utf-8') as f:
    f.write('''
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
''')
print('Appended meta-pets and tournament creation to board.py')
