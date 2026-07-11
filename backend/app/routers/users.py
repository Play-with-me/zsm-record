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

@router.put("/{user_id}/admin", response_model=schemas.UserResponse)
async def admin_update_user(
    user_id: str,
    user_update: schemas.UserAdminUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin)
) -> Any:
    from sqlalchemy.future import select
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    
    update_data = user_update.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    try:
        await db.commit()
        await db.refresh(user)
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Tên hoặc email đã tồn tại.")
    
    return user

@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user_profile(user_id: str, db: AsyncSession = Depends(get_db)) -> Any:
    from sqlalchemy.future import select
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    return user


@router.delete("/{user_id}")
async def admin_delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_admin: models.User = Depends(get_current_admin),
) -> Any:
    from sqlalchemy.future import select

    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")

    # Không cho admin tự xóa chính mình (tuỳ chọn)
    if user.id == current_admin.id:
        raise HTTPException(status_code=400, detail="Không thể xóa chính mình.")

    await db.delete(user)
    await db.commit()
    return {"message": "User deleted"}


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
    # Check 5-times per day cooldown
    if current_user.last_avatar_update:
        delta = datetime.utcnow() - current_user.last_avatar_update
        if delta.total_seconds() < 86400:
            if current_user.avatar_update_count >= 5:
                hours_left = 24 - int(delta.total_seconds() // 3600)
                raise HTTPException(status_code=400, detail=f"Bạn đã hết lượt đổi ảnh (tối đa 5 lần/ngày). Vui lòng thử lại sau {hours_left} giờ.")
            else:
                current_user.avatar_update_count += 1
        else:
            current_user.avatar_update_count = 1
    else:
        current_user.avatar_update_count = 1

    if not avatar_file.content_type or not avatar_file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File tải lên phải là hình ảnh hợp lệ.")

    cloudinary_url = os.getenv("CLOUDINARY_URL")
    image_url = None
    file_content = await avatar_file.read()
    
    if cloudinary_url and "your_api_key" not in cloudinary_url:
        import cloudinary
        import cloudinary.uploader
        from fastapi.concurrency import run_in_threadpool
        
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
            print(f"Cloudinary upload failed: {e}, falling back to local storage")
            pass

    if not image_url:
        # Local fallback
        filename_orig = avatar_file.filename if avatar_file.filename else "image.jpg"
        file_ext = os.path.splitext(filename_orig)[1]
        filename = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}{file_ext}"
        
        uploads_dir = os.path.join(os.getcwd(), "uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        filepath = os.path.join(uploads_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(file_content)
            
        image_url = f"/uploads/{filename}"

    current_user.avatar = image_url
    current_user.last_avatar_update = datetime.utcnow()
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user

@router.get("/me/notifications")
async def get_my_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    from sqlalchemy.future import select
    result = await db.execute(
        select(models.Notification)
        .filter(models.Notification.user_id == current_user.id)
        .order_by(models.Notification.created_at.desc())
        .limit(20)
    )
    notifs = result.scalars().all()
    return notifs

@router.put("/me/notifications/read")
async def mark_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    from sqlalchemy import update
    await db.execute(
        update(models.Notification)
        .where(models.Notification.user_id == current_user.id)
        .values(is_read=True)
    )
    await db.commit()
    return {"status": "ok"}
