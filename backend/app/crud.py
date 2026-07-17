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
    user = await db.get(models.User, user_id)
    if user:
        user.exp += 50
        user.coins += 20
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
    current_user_id: str = None,
    is_admin: bool = False
):
    query = select(models.Video).options(
        selectinload(models.Video.user),
        selectinload(models.Video.map),
        selectinload(models.Video.car),
        selectinload(models.Video.pet)
    ).order_by(desc(models.Video.created_at))

    if map_id:
        query = query.filter(models.Video.map_id == map_id)
    if car_id:
        query = query.filter(models.Video.car_id == car_id)
    if user_id:
        query = query.filter(models.Video.user_id == user_id)

    if not is_admin:
        if current_user_id:
            query = query.filter(
                or_(
                    models.Video.visibility == models.VisibilityEnum.PUBLIC,
                    models.Video.user_id == current_user_id
                )
            )
        else:
            query = query.filter(models.Video.visibility == models.VisibilityEnum.PUBLIC)

    if visibility is not None:
        query = query.filter(models.Video.visibility == visibility)

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

async def get_record_board_by_map(db: AsyncSession, map_id: str = None, car_id: str = None, pet_id: str = None):
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

    query = query.order_by(models.Video.map_id, asc(models.Video.record_ms))
    
    result = await db.execute(query)
    videos = result.scalars().all()
    
    map_groups = {}
    for video in videos:
        map_id = video.map_id
        if map_id not in map_groups:
            map_groups[map_id] = {
                "map": video.map,
                "records": []
            }
        
        rank = len(map_groups[map_id]["records"]) + 1
        
        map_groups[map_id]["records"].append({
            "rank": rank,
            "player": video.user,
            "car": video.car,
            "pet": video.pet,
            "record_ms": video.record_ms,
            "video_id": video.id,
            "video_url": video.video_url or "",
            "thumbnail": video.thumbnail
        })
        
    # Sort groups by map name or leave as is (dict values)
    return list(map_groups.values())

# --- Comments ---
async def get_comments_for_video(db: AsyncSession, video_id: str):
    result = await db.execute(
        select(models.Comment)
        .options(selectinload(models.Comment.user))
        .filter(models.Comment.video_id == video_id)
        .order_by(desc(models.Comment.created_at))
    )
    return result.scalars().all()

async def create_comment(db: AsyncSession, comment: schemas.CommentCreate, video_id: str, user_id: str):
    db_comment = models.Comment(
        video_id=video_id,
        user_id=user_id,
        content=comment.content
    )
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    
    # Eager load user
    result = await db.execute(
        select(models.Comment)
        .options(selectinload(models.Comment.user))
        .filter(models.Comment.id == db_comment.id)
    )
    return result.scalars().first()


async def get_comment(db: AsyncSession, comment_id: str):
    result = await db.execute(
        select(models.Comment).filter(models.Comment.id == comment_id)
    )
    return result.scalars().first()

async def delete_comment(db: AsyncSession, comment: models.Comment):
    await db.delete(comment)
    await db.commit()

# ---------------- SHOP & INVENTORY ----------------
async def get_shop_items(db: AsyncSession):
    result = await db.execute(select(models.ShopItem))
    return result.scalars().all()

async def get_user_items(db: AsyncSession, user_id: str):
    result = await db.execute(
        select(models.UserItem)
        .options(selectinload(models.UserItem.item))
        .filter(models.UserItem.user_id == user_id)
    )
    return result.scalars().all()

async def buy_item(db: AsyncSession, user_id: str, item_id: str):
    user = await db.get(models.User, user_id)
    item = await db.get(models.ShopItem, item_id)
    
    if not user or not item:
        return False, "User or Item not found"
        
    # Check if user already owns it
    result = await db.execute(
        select(models.UserItem)
        .filter(models.UserItem.user_id == user_id, models.UserItem.item_id == item_id)
    )
    if result.scalar_one_or_none():
        return False, "Bạn đã sở hữu vật phẩm này rồi"
        
    if user.role.value != 'ADMIN':
        if user.coins < item.price:
            return False, "Không đủ Z-Coins"
        user.coins -= item.price
    user_item = models.UserItem(user_id=user_id, item_id=item_id, is_equipped=False)
    db.add(user_item)
    await db.commit()
    return True, "Mua thành công"

async def equip_item(db: AsyncSession, user_id: str, user_item_id: str):
    user_item = await db.get(models.UserItem, user_item_id)
    if not user_item or user_item.user_id != user_id:
        return False, "Vật phẩm không tồn tại hoặc không thuộc về bạn"
        
    # We need the item_type to unequip others of same type
    item = await db.get(models.ShopItem, user_item.item_id)
    
    if user_item.is_equipped:
        # Just unequip
        user_item.is_equipped = False
    else:
        # Unequip others of the same type
        result = await db.execute(
            select(models.UserItem)
            .join(models.ShopItem)
            .filter(models.UserItem.user_id == user_id, models.ShopItem.item_type == item.item_type)
        )
        for ui in result.scalars().all():
            ui.is_equipped = False
        user_item.is_equipped = True
        
    await db.commit()
    return True, "Cập nhật thành công"


async def create_shop_item(db: AsyncSession, item: schemas.ShopItemCreate):
    db_item = models.ShopItem(**item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def update_shop_item(db: AsyncSession, item_id: str, item_update: schemas.ShopItemUpdate):
    result = await db.execute(select(models.ShopItem).filter(models.ShopItem.id == item_id))
    db_item = result.scalars().first()
    if not db_item:
        return None
        
    update_data = item_update.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
        
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def delete_shop_item(db: AsyncSession, item_id: str):
    from sqlalchemy import delete
    result = await db.execute(select(models.ShopItem).filter(models.ShopItem.id == item_id))
    db_item = result.scalars().first()
    if db_item:
        # Manually cascade delete user items first
        await db.execute(delete(models.UserItem).where(models.UserItem.item_id == item_id))
        await db.delete(db_item)
        await db.commit()
        return True
    return False
