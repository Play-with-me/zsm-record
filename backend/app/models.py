import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum, Boolean
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
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_username_update = Column(DateTime, nullable=True)
    last_avatar_update = Column(DateTime, nullable=True)
    avatar_update_count = Column(Integer, default=0)
    exp = Column(Integer, default=0)
    coins = Column(Integer, default=0)

    videos = relationship("Video", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    items = relationship("UserItem", back_populates="user", cascade="all, delete-orphan", lazy="selectin")

class ShopItem(Base):
    __tablename__ = "shop_items"
    
    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False, default=0)
    item_type = Column(String, nullable=False) # e.g. 'name_color', 'avatar_frame', 'badge'
    metadata_value = Column(String, nullable=False) # e.g. '#FF0000', or URL

class UserItem(Base):
    __tablename__ = "user_items"
    
    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String, ForeignKey("shop_items.id", ondelete="CASCADE"), nullable=False)
    is_equipped = Column(Boolean, default=False)
    purchased_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="items")
    item = relationship("ShopItem", lazy="selectin")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")

class TournamentFormatEnum(str, enum.Enum):
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"
    GROUPS = "GROUPS"

class TournamentStatusEnum(str, enum.Enum):
    DRAFT = "DRAFT"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"

class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    map_id = Column(String, ForeignKey("maps.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    format = Column(Enum(TournamentFormatEnum), default=TournamentFormatEnum.SINGLE, nullable=False)
    status = Column(Enum(TournamentStatusEnum), default=TournamentStatusEnum.DRAFT, nullable=False)

    map = relationship("Map")
    participants = relationship("TournamentParticipant", back_populates="tournament", cascade="all, delete-orphan")
    matches = relationship("TournamentMatch", back_populates="tournament", cascade="all, delete-orphan")

class TournamentParticipant(Base):
    __tablename__ = "tournament_participants"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    tournament_id = Column(String, ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    seed = Column(Integer, nullable=True) # Hạt giống
    created_at = Column(DateTime, default=datetime.utcnow)

    tournament = relationship("Tournament", back_populates="participants")
    user = relationship("User")

class TournamentMatch(Base):
    __tablename__ = "tournament_matches"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    tournament_id = Column(String, ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False)
    round_name = Column(String, nullable=False) # e.g. 'Tứ Kết', 'Bán Kết'
    round_sequence = Column(Integer, nullable=False, default=1) # 1, 2, 3 for ordering
    match_index = Column(Integer, nullable=False, default=0) # 0, 1, 2, 3 in the round
    player1_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    player2_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    winner_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    next_match_id = Column(String, ForeignKey("tournament_matches.id", ondelete="SET NULL"), nullable=True)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    tournament = relationship("Tournament", back_populates="matches")
    player1 = relationship("User", foreign_keys=[player1_id])
    player2 = relationship("User", foreign_keys=[player2_id])
    winner = relationship("User", foreign_keys=[winner_id])

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
    comments = relationship("Comment", back_populates="video", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    video_id = Column(String, ForeignKey("videos.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    video = relationship("Video", back_populates="comments")
    user = relationship("User", back_populates="comments")
