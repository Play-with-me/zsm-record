import os
import shutil
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from .. import crud, schemas, models
from ..database import get_db
from .auth import get_current_user, get_optional_current_user





router = APIRouter(prefix="/videos", tags=["videos"])

@router.post("", response_model=schemas.VideoResponse)
async def create_video(
    video: schemas.VideoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return await crud.create_video(db=db, video=video, user_id=current_user.id)

@router.get("", response_model=List[schemas.VideoResponse])
async def read_videos(
    skip: int = 0,
    limit: int = 20,
    map_id: Optional[str] = None,
    car_id: Optional[str] = None,
    user_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_optional_current_user),
):
    is_admin = current_user is not None and current_user.role == models.RoleEnum.ADMIN
    current_user_id = current_user.id if current_user else None

    videos = await crud.get_videos(
        db,
        skip=skip,
        limit=limit,
        map_id=map_id,
        car_id=car_id,
        user_id=user_id,
        visibility=None,
        current_user_id=current_user_id,
        is_admin=is_admin
    )
    return videos


@router.get("/{video_id}", response_model=schemas.VideoResponse)
async def read_video(
    video_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user),
):
    db_video = await crud.get_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")

    # Private: chỉ owner hoặc admin
    if db_video.visibility == models.VisibilityEnum.PRIVATE:
        if current_user is None or (db_video.user_id != current_user.id and current_user.role != models.RoleEnum.ADMIN):
            raise HTTPException(status_code=403, detail="Not authorized")


    db_video.views += 1
    await db.commit()
    await db.refresh(db_video)
    return db_video


@router.put("/{video_id}", response_model=schemas.VideoResponse)
async def update_video(
    video_id: str,
    video_update: schemas.VideoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_video = await crud.get_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    if db_video.user_id != current_user.id and current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = video_update.model_dump(exclude_none=True)
    if "video_url" in update_data:
        update_data["video_url"] = (update_data["video_url"] or "").strip()
    for key, value in update_data.items():
        setattr(db_video, key, value)
    
    await db.commit()
    await db.refresh(db_video)
    return db_video

@router.delete("/{video_id}")
async def delete_video(
    video_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_video = await crud.get_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    # Only owner or admin can delete
    if db_video.user_id != current_user.id and current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    await db.delete(db_video)
    await db.commit()
    return {"message": "Video deleted"}
