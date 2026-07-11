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

from fastapi import HTTPException

@router.put("/admin/maps/{map_id}", response_model=schemas.MapResponse)
async def update_map(
    map_id: str,
    map_in: schemas.MapCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    from sqlalchemy.future import select
    result = await db.execute(select(models.Map).filter(models.Map.id == map_id))
    m = result.scalars().first()
    if not m: raise HTTPException(status_code=404, detail="Map not found")
    m.name = map_in.name
    m.difficulty = map_in.difficulty
    await db.commit()
    await db.refresh(m)
    return m

@router.delete("/admin/maps/{map_id}")
async def delete_map(
    map_id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    from sqlalchemy.future import select
    result = await db.execute(select(models.Map).filter(models.Map.id == map_id))
    m = result.scalars().first()
    if not m: raise HTTPException(status_code=404, detail="Map not found")
    # Also delete videos? Actually cascade handles it if set up, or we can just delete it
    await db.delete(m)
    await db.commit()
    return {"message": "Deleted map"}

@router.put("/admin/cars/{car_id}", response_model=schemas.CarResponse)
async def update_car(
    car_id: str,
    car_in: schemas.CarCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    from sqlalchemy.future import select
    result = await db.execute(select(models.Car).filter(models.Car.id == car_id))
    c = result.scalars().first()
    if not c: raise HTTPException(status_code=404, detail="Car not found")
    c.name = car_in.name
    c.car_class = car_in.car_class
    await db.commit()
    await db.refresh(c)
    return c

@router.delete("/admin/cars/{car_id}")
async def delete_car(
    car_id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    from sqlalchemy.future import select
    result = await db.execute(select(models.Car).filter(models.Car.id == car_id))
    c = result.scalars().first()
    if not c: raise HTTPException(status_code=404, detail="Car not found")
    await db.delete(c)
    await db.commit()
    return {"message": "Deleted car"}

@router.put("/admin/pets/{pet_id}", response_model=schemas.PetResponse)
async def update_pet(
    pet_id: str,
    pet_in: schemas.PetCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    from sqlalchemy.future import select
    result = await db.execute(select(models.Pet).filter(models.Pet.id == pet_id))
    p = result.scalars().first()
    if not p: raise HTTPException(status_code=404, detail="Pet not found")
    p.name = pet_in.name
    await db.commit()
    await db.refresh(p)
    return p

@router.delete("/admin/pets/{pet_id}")
async def delete_pet(
    pet_id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
):
    from sqlalchemy.future import select
    result = await db.execute(select(models.Pet).filter(models.Pet.id == pet_id))
    p = result.scalars().first()
    if not p: raise HTTPException(status_code=404, detail="Pet not found")
    await db.delete(p)
    await db.commit()
    return {"message": "Deleted pet"}
