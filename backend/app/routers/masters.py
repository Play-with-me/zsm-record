from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import crud, schemas, models
from ..database import get_db
from .auth import get_current_admin

router = APIRouter(tags=["masters"])

# --- Maps ---
@router.get("/maps", response_model=List[schemas.MapResponse])
async def read_maps(db: AsyncSession = Depends(get_db)):
    return await crud.get_maps(db)

@router.post("/admin/maps", response_model=schemas.MapResponse)
async def create_map(
    map_in: schemas.MapCreate, 
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    return await crud.create_map(db=db, map_in=map_in)

# --- Cars ---
@router.get("/cars", response_model=List[schemas.CarResponse])
async def read_cars(db: AsyncSession = Depends(get_db)):
    return await crud.get_cars(db)

@router.post("/admin/cars", response_model=schemas.CarResponse)
async def create_car(
    car_in: schemas.CarCreate, 
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    return await crud.create_car(db=db, car_in=car_in)

# --- Pets ---
@router.get("/pets", response_model=List[schemas.PetResponse])
async def read_pets(db: AsyncSession = Depends(get_db)):
    return await crud.get_pets(db)

@router.post("/admin/pets", response_model=schemas.PetResponse)
async def create_pet(
    pet_in: schemas.PetCreate, 
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    return await crud.create_pet(db=db, pet_in=pet_in)
