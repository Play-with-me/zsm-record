import os
import shutil
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from .. import crud, schemas, models
from ..database import get_db
from .auth import get_current_user, get_current_admin

router = APIRouter(prefix="/videos", tags=["videos"])

@router.post("", response_model=schemas.VideoResponse)
async def create_video(
    map_id: str = Form(...),
    car_id: str = Form(...),
    pet_id: Optional[str] = Form(None),
    record_ms: int = Form(...),
    description: Optional[str] = Form(None),
    visibility: models.VisibilityEnum = Form(models.VisibilityEnum.PUBLIC),
    video_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    cloudinary_url = os.getenv("CLOUDINARY_URL")
    if cloudinary_url:
        import cloudinary
        import cloudinary.uploader
        from fastapi.concurrency import run_in_threadpool
        
        file_content = await video_file.read()
        
        def upload_to_cloudinary(content, fname):
            res = cloudinary.uploader.upload(
                content, 
                resource_type="video",
                public_id=fname
            )
            return res.get("secure_url")
            
        filename = str(uuid.uuid4())
        video_url = await run_in_threadpool(upload_to_cloudinary, file_content, filename)
    else:
        file_ext = os.path.splitext(video_file.filename)[1]
        filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join("uploads", filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(video_file.file, buffer)
        
        video_url = f"http://localhost:8001/uploads/{filename}"
    
    video_data = schemas.VideoCreate(
        map_id=map_id,
        car_id=car_id,
        pet_id=pet_id,
        record_ms=record_ms,
        video_url=video_url,
        description=description,
        visibility=visibility
    )
    return await crud.create_video(db=db, video=video_data, user_id=current_user.id)

@router.get("", response_model=List[schemas.VideoResponse])
async def read_videos(
    skip: int = 0,
    limit: int = 20,
    map_id: Optional[str] = None,
    car_id: Optional[str] = None,
    user_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    videos = await crud.get_videos(db, skip=skip, limit=limit, map_id=map_id, car_id=car_id, user_id=user_id)
    return videos

@router.get("/{video_id}", response_model=schemas.VideoResponse)
async def read_video(video_id: str, db: AsyncSession = Depends(get_db)):
    db_video = await crud.get_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
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
