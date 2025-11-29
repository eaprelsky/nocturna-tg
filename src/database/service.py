"""Database service for CRUD operations."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, BirthData

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Service for database operations.
    
    Handles all CRUD operations for users and birth data.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize database service.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def get_or_create_user(
        self, telegram_id: int, username: Optional[str] = None
    ) -> User:
        """
        Get existing user or create new one.
        
        Args:
            telegram_id: Telegram user ID
            username: Telegram username (optional)
            
        Returns:
            User instance
        """
        # Try to get existing user
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if user:
            # Update username if changed
            if username and user.username != username:
                user.username = username
                user.updated_at = datetime.utcnow()
                await self.session.commit()
                logger.info(f"Updated username for user {telegram_id}")
            return user

        # Create new user
        user = User(telegram_id=telegram_id, username=username)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        logger.info(f"Created new user: {telegram_id}")
        return user

    async def get_user(self, telegram_id: int) -> Optional[User]:
        """
        Get user by telegram ID.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            User instance or None
        """
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_birth_data(self, telegram_id: int) -> Optional[BirthData]:
        """
        Get birth data for user.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            BirthData instance or None
        """
        result = await self.session.execute(
            select(BirthData).where(BirthData.user_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def has_birth_data(self, telegram_id: int) -> bool:
        """
        Check if user has birth data.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            True if birth data exists, False otherwise
        """
        birth_data = await self.get_birth_data(telegram_id)
        return birth_data is not None

    async def save_birth_data(
        self,
        telegram_id: int,
        birth_date: str,
        birth_time: str,
        timezone: str,
        latitude: float,
        longitude: float,
        location_name: Optional[str] = None,
        chart_id: Optional[str] = None,
        natal_chart_cache: Optional[Dict[str, Any]] = None,
    ) -> BirthData:
        """
        Save or update birth data for user.
        
        Args:
            telegram_id: Telegram user ID
            birth_date: Birth date in YYYY-MM-DD format
            birth_time: Birth time in HH:MM:SS format
            timezone: Timezone name
            latitude: Geographic latitude
            longitude: Geographic longitude
            location_name: Human-readable location name
            chart_id: Chart ID from Nocturna API
            natal_chart_cache: Cached natal chart data
            
        Returns:
            BirthData instance
        """
        # Ensure user exists
        await self.get_or_create_user(telegram_id)

        # Check if birth data already exists
        existing = await self.get_birth_data(telegram_id)

        if existing:
            # Update existing birth data
            existing.birth_date = birth_date
            existing.birth_time = birth_time
            existing.timezone = timezone
            existing.latitude = latitude
            existing.longitude = longitude
            existing.location_name = location_name
            existing.chart_id = chart_id
            existing.natal_chart_cache = natal_chart_cache
            existing.updated_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(existing)
            logger.info(f"Updated birth data for user {telegram_id}")
            return existing

        # Create new birth data
        birth_data = BirthData(
            user_id=telegram_id,
            birth_date=birth_date,
            birth_time=birth_time,
            timezone=timezone,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            chart_id=chart_id,
            natal_chart_cache=natal_chart_cache,
        )
        self.session.add(birth_data)
        await self.session.commit()
        await self.session.refresh(birth_data)
        logger.info(f"Created birth data for user {telegram_id}")
        return birth_data

    async def update_natal_chart_cache(
        self, telegram_id: int, natal_chart_data: Dict[str, Any]
    ) -> None:
        """
        Update cached natal chart data.
        
        Args:
            telegram_id: Telegram user ID
            natal_chart_data: Natal chart calculation data
        """
        birth_data = await self.get_birth_data(telegram_id)
        if birth_data:
            birth_data.natal_chart_cache = natal_chart_data
            birth_data.updated_at = datetime.utcnow()
            await self.session.commit()
            logger.info(f"Updated natal chart cache for user {telegram_id}")

    async def update_preferences(
        self, telegram_id: int, preferences: Dict[str, Any]
    ) -> None:
        """
        Update user preferences.
        
        Args:
            telegram_id: Telegram user ID
            preferences: User preferences dictionary
        """
        birth_data = await self.get_birth_data(telegram_id)
        if birth_data:
            birth_data.preferences = preferences
            birth_data.updated_at = datetime.utcnow()
            await self.session.commit()
            logger.info(f"Updated preferences for user {telegram_id}")

    async def delete_birth_data(self, telegram_id: int) -> bool:
        """
        Delete birth data for user.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            True if deleted, False if not found
        """
        birth_data = await self.get_birth_data(telegram_id)
        if birth_data:
            await self.session.delete(birth_data)
            await self.session.commit()
            logger.info(f"Deleted birth data for user {telegram_id}")
            return True
        return False

    async def delete_user(self, telegram_id: int) -> bool:
        """
        Delete user and all associated data (cascade).
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            True if deleted, False if not found
        """
        user = await self.get_user(telegram_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()
            logger.info(f"Deleted user {telegram_id} and associated data")
            return True
        return False

    async def get_user_count(self) -> int:
        """
        Get total number of users.
        
        Returns:
            Number of users in database
        """
        result = await self.session.execute(select(User))
        users = result.scalars().all()
        return len(users)

    async def get_users_with_birth_data_count(self) -> int:
        """
        Get number of users with birth data.
        
        Returns:
            Number of users with birth data
        """
        result = await self.session.execute(select(BirthData))
        birth_data_list = result.scalars().all()
        return len(birth_data_list)

