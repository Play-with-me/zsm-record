from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_, desc, asc
from . import models, schemas
import bcrypt

def get_password_hash(password: str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# --- Users ---
async def get_user(db: AsyncSession, user_id: str):
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).filter(models.User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        avatar=user.avatar
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# --- Masters ---
async def get_maps(db: AsyncSession):
    result = await db.execute(select(models.Map))
    return result.scalars().all()

async def get_cars(db: AsyncSession):
    result = await db.execute(select(models.Car))
    return result.scalars().all()

async def get_pets(db: AsyncSession):
    result = await db.execute(select(models.Pet))
    return result.scalars().all()

async def create_map(db: AsyncSession, map_in: schemas.MapCreate):
    db_map = models.Map(**map_in.model_dump())
    db.add(db_map)
    await db.commit()
    await db.refresh(db_map)
    return db_map

async def create_car(db: AsyncSession, car_in: schemas.CarCreate):
    db_car = models.Car(**car_in.model_dump())
    db.add(db_car)
    await db.commit()
    await db.refresh(db_car)
    return db_car

async def create_pet(db: AsyncSession, pet_in: schemas.PetCreate):
    db_pet = models.Pet(**pet_in.model_dump())
    db.add(db_pet)
    await db.commit()
    await db.refresh(db_pet)
    return db_pet

from sqlalchemy.orm import selectinload

async def create_video(db: AsyncSession, video: schemas.VideoCreate, user_id: str):
    v_dump = video.model_dump()
    v_dump["video_url"] = (v_dump.get("video_url") or "").strip()
    v_dump["thumbnail"] = v_dump["thumbnail"].strip()
    db_video = models.Video(**v_dump, user_id=user_id)
    db.add(db_video)
    await db.commit()
    
    # Eager load relationships for response
    result = await db.execute(
        select(models.Video)
        .options(
            selectinload(models.Video.user),
            selectinload(models.Video.map),
            selectinload(models.Video.car),
            selectinload(models.Video.pet)
        )
        .filter(models.Video.id == db_video.id)
    )
    return result.scalars().first()

async def get_videos(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    map_id: str = None,
    car_id: str = None,
    user_id: str = None,
    visibility: models.VisibilityEnum = None,
):
    query = select(models.Video).options(
        selectinload(models.Video.user),
        selectinload(models.Video.map),
        selectinload(models.Video.car),
        selectinload(models.Video.pet)
    ).order_by(desc(models.Video.created_at))

    if visibility is not None:
        query = query.filter(models.Video.visibility == visibility)

    if map_id:
        query = query.filter(models.Video.map_id == map_id)
    if car_id:
        query = query.filter(models.Video.car_id == car_id)
    if user_id:
        query = query.filter(models.Video.user_id == user_id)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def get_video(db: AsyncSession, video_id: str):
    result = await db.execute(
        select(models.Video).options(
            selectinload(models.Video.user),
            selectinload(models.Video.map),
            selectinload(models.Video.car),
            selectinload(models.Video.pet)
        ).filter(models.Video.id == video_id)
    )
    return result.scalars().first()

async def get_record_board(db: AsyncSession, map_id: str = None, car_id: str = None, pet_id: str = None):
    query = select(models.Video).options(
        selectinload(models.Video.user),
        selectinload(models.Video.map),
        selectinload(models.Video.car),
        selectinload(models.Video.pet)
    ).filter(models.Video.visibility == models.VisibilityEnum.PUBLIC)
    
    if map_id:
        query = query.filter(models.Video.map_id == map_id)
    if car_id:
        query = query.filter(models.Video.car_id == car_id)
    if pet_id:
        query = query.filter(models.Video.pet_id == pet_id)
        
    query = query.order_by(asc(models.Video.record_ms))
    query = query.limit(100)
    
    result = await db.execute(query)
    videos = result.scalars().all()
    
    board = []
    for rank, video in enumerate(videos, start=1):
        board.append({
            "rank": rank,
            "player": video.user,
            "car": video.car,
            "pet": video.pet,
            "record_ms": video.record_ms,
            "video_id": video.id,
            "video_url": video.video_url or "",
            "thumbnail": video.thumbnail
        })
    return board
