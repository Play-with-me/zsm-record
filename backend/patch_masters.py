import os

file_path = 'app/routers/masters.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add endpoints for Maps
maps_endpoints = '''
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
'''

# Add endpoints for Cars
cars_endpoints = '''
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
'''

# Add endpoints for Pets
pets_endpoints = '''
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
'''

if "def update_map" not in content:
    content += "\nfrom fastapi import HTTPException\n"
    content += maps_endpoints
    content += cars_endpoints
    content += pets_endpoints

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated masters.py")
