import os

file_path = 'app/routers/users.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

users_endpoints = '''
from pydantic import BaseModel
class UserAdminUpdate(BaseModel):
    role: str

@router.put("/admin/users/{u_id}")
async def update_user_admin(
    u_id: str,
    u_in: UserAdminUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    from sqlalchemy.future import select
    result = await db.execute(select(models.User).filter(models.User.id == u_id))
    u_obj = result.scalars().first()
    if not u_obj: raise HTTPException(status_code=404, detail="User not found")
    
    # Just update role for now
    if u_in.role in ["ADMIN", "USER"]:
        u_obj.role = models.RoleEnum[u_in.role]
        await db.commit()
        await db.refresh(u_obj)
    return u_obj

@router.delete("/admin/users/{u_id}")
async def delete_user_admin(
    u_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.role != models.RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    from sqlalchemy.future import select
    result = await db.execute(select(models.User).filter(models.User.id == u_id))
    u_obj = result.scalars().first()
    if not u_obj: raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(u_obj)
    await db.commit()
    return {"message": "Deleted user"}
'''

if "def update_user_admin" not in content:
    content += users_endpoints

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated users.py")
