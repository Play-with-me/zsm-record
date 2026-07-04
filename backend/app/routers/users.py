import os
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from .auth import get_current_user, get_db, get_current_admin
from .. import schemas, models

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[schemas.UserResponse])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
) -> Any:
    from sqlalchemy.future import select
    result = await db.execute(select(models.User).order_by(models.User.created_at.desc()))
    return result.scalars().all()


@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user_profile(user_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    from sqlalchemy.future import select
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    return user

@router.put("/me/username", response_model=schemas.UserResponse)
async def update_username(
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    # Check 7-day cooldown
    if current_user.last_username_update:
        delta = datetime.utcnow() - current_user.last_username_update
        if delta < timedelta(days=7):
            days_left = 7 - delta.days
            raise HTTPException(status_code=400, detail=f"Bạn chỉ được đổi tên 1 lần mỗi tuần. Vui lòng thử lại sau {days_left} ngày.")

    if len(user_update.username) < 3:
         raise HTTPException(status_code=400, detail="Tên người dùng phải có ít nhất 3 ký tự.")

    current_user.username = user_update.username
    current_user.last_username_update = datetime.utcnow()
    
    try:
        await db.commit()
        await db.refresh(current_user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Tên người dùng đã tồn tại hoặc có lỗi xảy ra.")
        
    return current_user

@router.post("/me/avatar", response_model=schemas.UserResponse)
async def update_avatar(
    avatar_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    # Check 1-day cooldown
    if current_user.last_avatar_update:
        delta = datetime.utcnow() - current_user.last_avatar_update
        if delta < timedelta(days=1):
            hours_left = 24 - (delta.seconds // 3600)
            raise HTTPException(status_code=400, detail=f"Bạn chỉ được đổi ảnh đại diện 1 lần mỗi ngày. Vui lòng thử lại sau {hours_left} giờ.")

    if not avatar_file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File tải lên phải là hình ảnh.")

    cloudinary_url = os.getenv("CLOUDINARY_URL")
    if cloudinary_url:
        import cloudinary
        import cloudinary.uploader
        from fastapi.concurrency import run_in_threadpool
        
        file_content = await avatar_file.read()
        
        def upload_to_cloudinary(content, fname):
            res = cloudinary.uploader.upload(
                content, 
                resource_type="image",
                public_id=fname,
                folder="avatars"
            )
            return res.get("secure_url")
            
        filename = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}"
        try:
            image_url = await run_in_threadpool(upload_to_cloudinary, file_content, filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi tải lên ảnh: {str(e)}")
    else:
        # Local fallback
        file_ext = os.path.splitext(avatar_file.filename)[1]
        filename = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}{file_ext}"
        
        uploads_dir = os.path.join(os.getcwd(), "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        filepath = os.path.join(uploads_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(await avatar_file.read())
            
        image_url = f"/uploads/{filename}"

    current_user.avatar = image_url
    current_user.last_avatar_update = datetime.utcnow()
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user
