"""SQLAlchemy models for Nocturna Telegram Bot."""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    """
    User model for storing Telegram user data.
    
    Stores minimal user information to comply with privacy requirements.
    Only telegram_id is required for user identification.
    """
    
    __tablename__ = "users"

    telegram_id = Column(
        BigInteger,
        primary_key=True,
        unique=True,
        index=True,
        comment="Telegram user ID (unique identifier)"
    )
    username = Column(
        String(255),
        nullable=True,
        comment="Telegram username (optional, for convenience)"
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Account creation timestamp"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )

    # Relationship
    birth_data = relationship(
        "BirthData",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"


class BirthData(Base):
    """
    Birth data model for storing user's natal chart information.
    
    Stores birth date, time, location for natal chart calculations.
    Includes JSONB fields for flexible data storage and caching.
    """
    
    __tablename__ = "birth_data"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    user_id = Column(
        BigInteger,
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
        comment="Foreign key to users table"
    )
    
    # Nocturna API chart ID
    chart_id = Column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
        comment="Chart ID from Nocturna API"
    )

    # Birth date and time
    birth_date = Column(
        String(10),
        nullable=False,
        comment="Birth date in YYYY-MM-DD format"
    )
    birth_time = Column(
        String(8),
        nullable=False,
        comment="Birth time in HH:MM:SS format"
    )
    timezone = Column(
        String(50),
        nullable=False,
        comment="Timezone name (e.g., 'Europe/Moscow')"
    )

    # Location
    location_name = Column(
        String(255),
        nullable=True,
        comment="Human-readable location name (e.g., 'Москва, Россия')"
    )
    latitude = Column(
        Float,
        nullable=False,
        comment="Geographic latitude"
    )
    longitude = Column(
        Float,
        nullable=False,
        comment="Geographic longitude"
    )

    # Additional data stored as JSONB for flexibility
    natal_chart_cache = Column(
        JSONB,
        nullable=True,
        comment="Cached natal chart calculation data"
    )
    preferences = Column(
        JSONB,
        nullable=True,
        comment="User preferences (aspect orbs, display settings, etc.)"
    )

    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Birth data creation timestamp"
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )

    # Relationship
    user = relationship("User", back_populates="birth_data")

    def __repr__(self) -> str:
        return (
            f"<BirthData(user_id={self.user_id}, "
            f"birth_date={self.birth_date}, "
            f"location={self.location_name})>"
        )

