import os

file_path = 'app/routers/board.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

tournaments_endpoints = '''
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
'''

if "def update_tournament" not in content:
    content += tournaments_endpoints

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated board.py")
