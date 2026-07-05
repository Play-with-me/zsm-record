from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from .models import RoleEnum, VisibilityEnum

# ----------------- Users -----------------
class UserBase(BaseModel):
    username: str
    email: EmailStr
    avatar: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    role: RoleEnum
    is_active: bool = True
    created_at: datetime
    last_username_update: Optional[datetime] = None
    last_avatar_update: Optional[datetime] = None
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: str

class UserAdminUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

# ----------------- Auth -----------------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# ----------------- Map -----------------
class MapBase(BaseModel):
    name: str
    difficulty: int = 1
    image: Optional[str] = None

class MapCreate(MapBase):
    pass

class MapResponse(MapBase):
    id: str
    class Config:
        from_attributes = True

# ----------------- Car -----------------
class CarBase(BaseModel):
    name: str
    car_class: str
    image: Optional[str] = None

class CarCreate(CarBase):
    pass

class CarResponse(CarBase):
    id: str
    class Config:
        from_attributes = True

# ----------------- Pet -----------------
class PetBase(BaseModel):
    name: str
    image: Optional[str] = None

class PetCreate(PetBase):
    pass

class PetResponse(PetBase):
    id: str
    class Config:
        from_attributes = True

# ----------------- Video -----------------
class VideoBase(BaseModel):
    map_id: str
    car_id: str
    pet_id: Optional[str] = None
    record_ms: int = Field(gt=0)
    video_url: Optional[str] = None
    thumbnail: Optional[str] = None
    description: Optional[str] = None
    visibility: VisibilityEnum = VisibilityEnum.PUBLIC

class VideoCreate(VideoBase):
    thumbnail: str = Field(min_length=1)

class VideoUpdate(BaseModel):
    map_id: Optional[str] = None
    car_id: Optional[str] = None
    pet_id: Optional[str] = None
    record_ms: Optional[int] = Field(None, gt=0)
    video_url: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[VisibilityEnum] = None

class VideoResponse(VideoBase):
    id: str
    user_id: str
    views: int
    likes: int
    created_at: datetime
    
    user: UserResponse
    map: MapResponse
    car: CarResponse
    pet: Optional[PetResponse]
    class Config:
        from_attributes = True

# ----------------- Record Board -----------------
class RecordBoardEntry(BaseModel):
    rank: int
    player: UserResponse
    car: CarResponse
    pet: Optional[PetResponse]
    record_ms: int
    video_id: str
    video_url: Optional[str] = None
    thumbnail: Optional[str] = None
    class Config:
        from_attributes = True
