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
