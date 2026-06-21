from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum, JSON, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum


class UserRole(str, enum.Enum):
    PLAYER = "player"
    STORE_OWNER = "store_owner"
    DM = "dm"
    ADMIN = "admin"


class ScriptType(str, enum.Enum):
    SUSPENSE = "suspense"
    HORROR = "horror"
    EMOTION = "emotion"
    REASONING = "reasoning"
    HAPPY = "happy"
    SCI_FI = "sci_fi"
    ANCIENT = "ancient"
    MODERN = "modern"


class DifficultyLevel(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class GameStatus(str, enum.Enum):
    RECRUITING = "recruiting"
    FULL = "full"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AssignmentMethod(str, enum.Enum):
    RANDOM = "random"
    MANUAL = "manual"


class PostType(str, enum.Enum):
    RECOMMENDATION = "recommendation"
    REVIEW = "review"
    SECOND_HAND = "second_hand"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"


class IncomeType(str, enum.Enum):
    SESSION = "session"
    COMMISSION = "commission"
    BONUS = "bonus"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone = Column(String(20))
    avatar = Column(String(255))
    nickname = Column(String(50))
    gender = Column(Enum(Gender), default=Gender.UNKNOWN)
    birthday = Column(Date)
    role = Column(Enum(UserRole), default=UserRole.PLAYER, nullable=False)
    bio = Column(Text)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    dm_profile = relationship("DMProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    store_profile = relationship("StoreProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    games_created = relationship("Game", back_populates="creator", foreign_keys="Game.creator_id")
    games_participated = relationship("GameParticipant", back_populates="user", cascade="all, delete-orphan")
    character_assignments = relationship("CharacterAssignment", back_populates="user", foreign_keys="CharacterAssignment.user_id", cascade="all, delete-orphan")
    reviews_written = relationship("Review", back_populates="author", foreign_keys="Review.author_id", cascade="all, delete-orphan")
    reviews_received = relationship("Review", back_populates="target_user", foreign_keys="Review.target_user_id", cascade="all, delete-orphan")
    posts = relationship("CommunityPost", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")

class DMProfile(Base):
    __tablename__ = "dm_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    real_name = Column(String(50))
    id_card = Column(String(20))
    experience_years = Column(Integer, default=0)
    description = Column(Text)
    good_script_types = Column(JSON)
    average_rating = Column(Float, default=0.0)
    total_games = Column(Integer, default=0)
    is_approved = Column(Boolean, default=False)
    total_income = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="dm_profile")
    schedules = relationship("DMSchedule", back_populates="dm", cascade="all, delete-orphan")
    games_hosted = relationship("Game", back_populates="dm", foreign_keys="Game.dm_id")
    income_records = relationship("DMIncomeRecord", back_populates="dm", cascade="all, delete-orphan")


class StoreProfile(Base):
    __tablename__ = "store_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    store_name = Column(String(100), nullable=False)
    store_address = Column(String(255), nullable=False)
    store_phone = Column(String(20))
    business_license = Column(String(100))
    description = Column(Text)
    opening_hours = Column(JSON)
    average_rating = Column(Float, default=0.0)
    total_games = Column(Integer, default=0)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="store_profile")
    scripts = relationship("Script", back_populates="store", cascade="all, delete-orphan")
    games_hosted = relationship("Game", back_populates="store", foreign_keys="Game.store_id")

class DMSchedule(Base):
    __tablename__ = "dm_schedules"

    id = Column(Integer, primary_key=True, index=True)
    dm_id = Column(Integer, ForeignKey("dm_profiles.id"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    dm = relationship("DMProfile", back_populates="schedules")
    game = relationship("Game", back_populates="schedule")


class Script(Base):
    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    script_type = Column(Enum(ScriptType), nullable=False)
    difficulty = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    min_players = Column(Integer, nullable=False)
    max_players = Column(Integer, nullable=False)
    estimated_duration = Column(Integer, nullable=False)
    cover_image = Column(String(255))
    images = Column(JSON)
    price = Column(Float, default=0.0)
    author = Column(String(100))
    publisher = Column(String(100))
    publish_year = Column(Integer)
    store_id = Column(Integer, ForeignKey("store_profiles.id"))
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    store = relationship("StoreProfile", back_populates="scripts")
    characters = relationship("Character", back_populates="script", cascade="all, delete-orphan")
    games = relationship("Game", back_populates="script", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="script", cascade="all, delete-orphan")


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=False)
    name = Column(String(100), nullable=False)
    gender = Column(Enum(Gender), default=Gender.UNKNOWN)
    age = Column(Integer)
    description = Column(Text)
    background_story = Column(Text)
    avatar = Column(String(255))
    is_lead = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    script = relationship("Script", back_populates="characters")
    assignments = relationship("CharacterAssignment", back_populates="character", cascade="all, delete-orphan")

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    script_id = Column(Integer, ForeignKey("scripts.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("store_profiles.id"))
    dm_id = Column(Integer, ForeignKey("dm_profiles.id"))
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time)
    duration = Column(Integer)
    max_players = Column(Integer, nullable=False)
    current_players = Column(Integer, default=0)
    status = Column(Enum(GameStatus), default=GameStatus.RECRUITING)
    assignment_method = Column(Enum(AssignmentMethod), default=AssignmentMethod.MANUAL)
    price_per_person = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)
    location = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    script = relationship("Script", back_populates="games")
    store = relationship("StoreProfile", back_populates="games_hosted")
    dm = relationship("DMProfile", back_populates="games_hosted")
    creator = relationship("User", back_populates="games_created", foreign_keys=[creator_id])
    schedule = relationship("DMSchedule", back_populates="game", uselist=False)
    participants = relationship("GameParticipant", back_populates="game", cascade="all, delete-orphan")
    character_assignments = relationship("CharacterAssignment", back_populates="game", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="game", cascade="all, delete-orphan")


class GameParticipant(Base):
    __tablename__ = "game_participants"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    has_paid = Column(Boolean, default=False)
    payment_amount = Column(Float, default=0.0)
    payment_time = Column(DateTime(timezone=True))
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)

    game = relationship("Game", back_populates="participants")
    user = relationship("User", back_populates="games_participated")

class CharacterAssignment(Base):
    __tablename__ = "character_assignments"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_by = Column(Integer, ForeignKey("users.id"))

    game = relationship("Game", back_populates="character_assignments")
    user = relationship("User", back_populates="character_assignments", foreign_keys=[user_id])
    character = relationship("Character", back_populates="assignments")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    script_id = Column(Integer, ForeignKey("scripts.id"))
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Float, nullable=False)
    content = Column(Text)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    game = relationship("Game", back_populates="reviews")
    script = relationship("Script", back_populates="reviews")
    author = relationship("User", back_populates="reviews_written", foreign_keys=[author_id])
    target_user = relationship("User", back_populates="reviews_received", foreign_keys=[target_user_id])


class CommunityPost(Base):
    __tablename__ = "community_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    post_type = Column(Enum(PostType), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    script_id = Column(Integer, ForeignKey("scripts.id"))
    images = Column(JSON)
    tags = Column(JSON)
    is_hot = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    is_approved = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("community_posts.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"))
    content = Column(Text, nullable=False)
    like_count = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    post = relationship("CommunityPost", back_populates="comments")
    author = relationship("User", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")


class DMIncomeRecord(Base):
    __tablename__ = "dm_income_records"

    id = Column(Integer, primary_key=True, index=True)
    dm_id = Column(Integer, ForeignKey("dm_profiles.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    notes = Column(Text)
    settled_at = Column(DateTime(timezone=True), server_default=func.now())

    dm = relationship("DMProfile", back_populates="income_records")
    game = relationship("Game")


class CommunityLike(Base):
    __tablename__ = "community_likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("community_posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship("CommunityPost")
    user = relationship("User")
