import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from .database import Base

def generate_uuid():
    return str(uuid.uuid4())

class RoleEnum(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class VisibilityEnum(str, enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.USER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_username_update = Column(DateTime, nullable=True)
    last_avatar_update = Column(DateTime, nullable=True)

    videos = relationship("Video", back_populates="user")

class Map(Base):
    __tablename__ = "maps"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    name = Column(String, unique=True, index=True, nullable=False)
    difficulty = Column(Integer, nullable=False, default=1)
    image = Column(String, nullable=True)

    videos = relationship("Video", back_populates="map")

class Car(Base):
    __tablename__ = "cars"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    name = Column(String, unique=True, index=True, nullable=False)
    car_class = Column(String, nullable=False) # e.g. 'A', 'T' (using car_class because class is keyword)
    image = Column(String, nullable=True)

    videos = relationship("Video", back_populates="car")

class Pet(Base):
    __tablename__ = "pets"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    name = Column(String, unique=True, index=True, nullable=False)
    image = Column(String, nullable=True)

    videos = relationship("Video", back_populates="pet")

class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    map_id = Column(String, ForeignKey("maps.id"), nullable=False)
    car_id = Column(String, ForeignKey("cars.id"), nullable=False)
    pet_id = Column(String, ForeignKey("pets.id"), nullable=True)
    
    record_ms = Column(Integer, nullable=False)
    video_url = Column(String, nullable=False)
    thumbnail = Column(String, nullable=True)
    description = Column(String, nullable=True)
    visibility = Column(Enum(VisibilityEnum), default=VisibilityEnum.PUBLIC, nullable=False)
    
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="videos")
    map = relationship("Map", back_populates="videos")
    car = relationship("Car", back_populates="videos")
    pet = relationship("Pet", back_populates="videos")
