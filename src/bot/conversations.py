"""Conversation handlers for collecting user birth data."""

import logging
import re
from datetime import datetime
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from timezonefinder import TimezoneFinder

from src.database.service import DatabaseService
from src.database.database import get_session
from src.api.nocturna_client import NocturnaClient

logger = logging.getLogger(__name__)


# Conversation states
(
    BIRTH_DATE,
    BIRTH_TIME,
    BIRTH_LOCATION,
    CONFIRM_DATA,
) = range(4)


class BirthDataConversation:
    """Handles conversation for collecting user birth data."""

    def __init__(self, nocturna_client: NocturnaClient):
        """
        Initialize birth data conversation handler.
        
        Args:
            nocturna_client: Client for Nocturna API
        """
        self.nocturna_client = nocturna_client
        self.geolocator = Nominatim(user_agent="nocturna-tg-bot/1.0")
        self.tf = TimezoneFinder()

    async def start_natal_setup(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """
        Start natal chart setup conversation.
        
        Args:
            update: Telegram update object
            context: Telegram context object
            
        Returns:
            Next conversation state
        """
        user = update.effective_user
        logger.info(f"User {user.id} started natal chart setup")

        # Check if user already has birth data
        async for session in get_session():
            db_service = DatabaseService(session)
            has_data = await db_service.has_birth_data(user.id)
        
        if has_data:
            message = (
                "У вас уже сохранена натальная карта.\n\n"
                "Если вы хотите изменить данные, продолжите настройку.\n"
                "Для отмены используйте /cancel\n\n"
            )
        else:
            message = (
                "🌟 <b>Настройка натальной карты</b>\n\n"
                "Для построения вашей натальной карты мне нужны следующие данные:\n"
                "• Дата рождения\n"
                "• Время рождения\n"
                "• Место рождения\n\n"
                "Эти данные будут надежно сохранены и использованы только для "
                "астрологических расчетов.\n\n"
                "Для отмены используйте /cancel\n\n"
            )

        message += "📅 <b>Введите дату рождения</b>\n"
        message += "<i>Формат: ДД.ММ.ГГГГ или ГГГГ-ММ-ДД</i>\n"
        message += "<i>Пример: 15.03.1990 или 1990-03-15</i>"

        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
        return BIRTH_DATE

    async def receive_birth_date(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """
        Receive and validate birth date.
        
        Args:
            update: Telegram update object
            context: Telegram context object
            
        Returns:
            Next conversation state
        """
        user_input = update.message.text.strip()
        
        # Try to parse date
        birth_date = self._parse_date(user_input)
        
        if not birth_date:
            await update.message.reply_text(
                "❌ Неверный формат даты.\n\n"
                "Пожалуйста, используйте формат:\n"
                "• ДД.ММ.ГГГГ (например: 15.03.1990)\n"
                "• ГГГГ-ММ-ДД (например: 1990-03-15)\n\n"
                "Или /cancel для отмены."
            )
            return BIRTH_DATE

        # Validate date range (1900-2025)
        try:
            date_obj = datetime.strptime(birth_date, "%Y-%m-%d")
            if date_obj.year < 1900 or date_obj.year > 2025:
                await update.message.reply_text(
                    "❌ Год рождения должен быть между 1900 и 2025.\n\n"
                    "Введите корректную дату или /cancel для отмены."
                )
                return BIRTH_DATE
        except ValueError:
            await update.message.reply_text(
                "❌ Некорректная дата.\n\n"
                "Введите существующую дату или /cancel для отмены."
            )
            return BIRTH_DATE

        # Save date to context
        context.user_data["birth_date"] = birth_date
        
        logger.info(f"User {update.effective_user.id} entered birth date: {birth_date}")

        message = (
            f"✅ Дата рождения: {self._format_date_ru(birth_date)}\n\n"
            "🕐 <b>Введите время рождения</b>\n"
            "<i>Формат: ЧЧ:ММ (24-часовой формат)</i>\n"
            "<i>Пример: 14:30 или 09:15</i>\n\n"
            "💡 Если не знаете точное время, укажите приблизительное или 12:00"
        )
        
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
        return BIRTH_TIME

    async def receive_birth_time(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """
        Receive and validate birth time.
        
        Args:
            update: Telegram update object
            context: Telegram context object
            
        Returns:
            Next conversation state
        """
        user_input = update.message.text.strip()
        
        # Try to parse time
        birth_time = self._parse_time(user_input)
        
        if not birth_time:
            await update.message.reply_text(
                "❌ Неверный формат времени.\n\n"
                "Пожалуйста, используйте формат ЧЧ:ММ\n"
                "Примеры: 14:30, 09:15, 00:00\n\n"
                "Или /cancel для отмены."
            )
            return BIRTH_TIME

        # Save time to context
        context.user_data["birth_time"] = birth_time
        
        logger.info(f"User {update.effective_user.id} entered birth time: {birth_time}")

        message = (
            f"✅ Время рождения: {birth_time}\n\n"
            "📍 <b>Введите место рождения</b>\n"
            "<i>Укажите город и страну</i>\n"
            "<i>Пример: Москва, Россия</i>\n\n"
            "💡 Для точных расчетов нужны координаты места рождения"
        )
        
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
        return BIRTH_LOCATION

    async def receive_birth_location(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """
        Receive birth location and geocode it.
        
        Args:
            update: Telegram update object
            context: Telegram context object
            
        Returns:
            Next conversation state
        """
        location_name = update.message.text.strip()
        
        if len(location_name) < 3:
            await update.message.reply_text(
                "❌ Слишком короткое название места.\n\n"
                "Пожалуйста, укажите город и страну.\n"
                "Например: Москва, Россия\n\n"
                "Или /cancel для отмены."
            )
            return BIRTH_LOCATION

        # Geocode using Nominatim (OpenStreetMap)
        processing_msg = await update.message.reply_text(
            "🔍 Ищу координаты места рождения..."
        )

        try:
            # Geocode with timeout
            location = self.geolocator.geocode(
                location_name,
                timeout=10,
                language="ru",
                addressdetails=True
            )
            
            if not location:
                await processing_msg.edit_text(
                    "❌ Место не найдено.\n\n"
                    "Попробуйте указать более точно:\n"
                    "• Добавьте название страны (например: Москва, Россия)\n"
                    "• Используйте латинское написание\n"
                    "• Укажите более крупный город\n\n"
                    "Или /cancel для отмены."
                )
                return BIRTH_LOCATION

            latitude = location.latitude
            longitude = location.longitude
            display_name = location.address
            
            # Use timezonefinder for accurate timezone
            timezone_str = self.tf.timezone_at(lng=longitude, lat=latitude)
            if not timezone_str:
                timezone_str = "UTC"  # Fallback if timezonefinder fails
                logger.warning(f"Could not determine timezone for {latitude}, {longitude}. Falling back to UTC.")

            # Save location data to context
            context.user_data["location_name"] = display_name
            context.user_data["latitude"] = latitude
            context.user_data["longitude"] = longitude
            context.user_data["timezone_str"] = timezone_str

            logger.info(
                f"User {update.effective_user.id} selected location: "
                f"{display_name} ({latitude}, {longitude}). Timezone: {timezone_str}"
            )

            await processing_msg.delete()

            # Show confirmation
            birth_date = context.user_data.get("birth_date", "")
            birth_time = context.user_data.get("birth_time", "")

            message = (
                "✅ <b>Проверьте введенные данные:</b>\n\n"
                f"📅 Дата: {self._format_date_ru(birth_date)}\n"
                f"🕐 Время: {birth_time}\n"
                f"📍 Место: {display_name}\n"
                f"🌍 Координаты: {latitude:.4f}, {longitude:.4f}\n"
                f"🕰 Часовой пояс: {timezone_str}\n\n"
                "Все верно? Ответьте:\n"
                "• <b>Да</b> - сохранить данные\n"
                "• <b>Нет</b> - начать заново (/natal)\n"
                "• /cancel - отменить"
            )

            await update.message.reply_text(message, parse_mode=ParseMode.HTML)
            return CONFIRM_DATA

        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Geocoding service error: {str(e)}")
            await processing_msg.edit_text(
                "❌ Сервис геокодирования временно недоступен.\n\n"
                "Попробуйте позже или используйте /cancel для отмены."
            )
            return BIRTH_LOCATION
        except Exception as e:
            logger.error(f"Error geocoding location: {str(e)}")
            await processing_msg.edit_text(
                "❌ Ошибка при поиске места.\n\n"
                "Попробуйте еще раз или используйте /cancel для отмены."
            )
            return BIRTH_LOCATION

    async def confirm_and_save(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """
        Confirm and save birth data.
        
        Args:
            update: Telegram update object
            context: Telegram context object
            
        Returns:
            ConversationHandler.END
        """
        user_input = update.message.text.strip().lower()
        
        if user_input not in ["да", "yes", "ок", "ok", "сохранить"]:
            await update.message.reply_text(
                "❌ Настройка отменена.\n\n"
                "Для повторной настройки используйте /natal"
            )
            context.user_data.clear()
            return ConversationHandler.END

        user_id = update.effective_user.id
        
        # Get data from context
        birth_date = context.user_data.get("birth_date")
        birth_time = context.user_data.get("birth_time")
        location_name = context.user_data.get("location_name")
        latitude = context.user_data.get("latitude")
        longitude = context.user_data.get("longitude")
        timezone_str = context.user_data.get("timezone_str")

        # Save to database
        processing_msg = await update.message.reply_text("💾 Сохраняю данные...")

        try:
            # Calculate chart using direct calculation endpoints
            birth_time_full = birth_time + ":00"  # Add seconds
            
            logger.info(f"Calculating natal chart for user {user_id} using direct calculation endpoints")
            
            # Use direct calculation endpoints instead of creating a stored chart
            positions_result = self.nocturna_client.calculate_planetary_positions(
                date=birth_date,
                time=birth_time_full,
                latitude=latitude,
                longitude=longitude,
                timezone=timezone_str,
            )
            
            houses_result = self.nocturna_client.calculate_houses_direct(
                date=birth_date,
                time=birth_time_full,
                latitude=latitude,
                longitude=longitude,
                timezone=timezone_str,
            )
            
            aspects_result = self.nocturna_client.calculate_aspects_direct(
                date=birth_date,
                time=birth_time_full,
                latitude=latitude,
                longitude=longitude,
                timezone=timezone_str,
            )
            
            # Build complete chart data from direct calculations
            complete_chart_data = {
                "date": birth_date,
                "time": birth_time_full,
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone_str,
                "positions": positions_result.get("positions", []),
                "houses": houses_result.get("houses", []),
                "aspects": aspects_result.get("aspects", []),
                "calculated_at": None,  # Will be set by database
            }
            
            logger.info(f"Successfully calculated natal chart for user {user_id}")
            logger.debug(f"Calculated {len(complete_chart_data.get('positions', []))} positions, "
                        f"{len(complete_chart_data.get('houses', []))} houses, "
                        f"{len(complete_chart_data.get('aspects', []))} aspects")

            # Now save to database with cached chart data
            async for session in get_session():
                db_service = DatabaseService(session)
                await db_service.save_birth_data(
                    telegram_id=user_id,
                    birth_date=birth_date,
                    birth_time=birth_time_full,
                    timezone=timezone_str,
                    location_name=location_name,
                    latitude=latitude,
                    longitude=longitude,
                    chart_id=None,  # No chart_id needed with direct calculations
                    natal_chart_cache=complete_chart_data,  # Cache the complete chart data
                )
                break

            await processing_msg.edit_text(
                "✅ <b>Данные успешно сохранены!</b>\n\n"
                "Теперь вам доступны:\n"
                "• /my_natal - посмотреть натальную карту\n"
                "• /my_transit - персональные транзиты\n"
                "• /profile - просмотр сохраненных данных\n\n"
                "🌟 Начните с команды /my_natal",
                parse_mode=ParseMode.HTML
            )

            logger.info(f"Saved birth data for user {user_id}")

        except Exception as e:
            logger.error(f"Error saving birth data: {str(e)}", exc_info=True)
            await processing_msg.edit_text(
                "❌ Ошибка при сохранении данных.\n\n"
                f"Детали: {str(e)}\n\n"
                "Пожалуйста, попробуйте позже или обратитесь к администратору."
            )

        context.user_data.clear()
        return ConversationHandler.END

    async def cancel_conversation(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int:
        """
        Cancel conversation.
        
        Args:
            update: Telegram update object
            context: Telegram context object
            
        Returns:
            ConversationHandler.END
        """
        await update.message.reply_text(
            "❌ Настройка отменена.\n\n"
            "Для повторной настройки используйте /natal"
        )
        context.user_data.clear()
        logger.info(f"User {update.effective_user.id} cancelled natal setup")
        return ConversationHandler.END

    @staticmethod
    def _parse_date(date_str: str) -> Optional[str]:
        """Parse date string to YYYY-MM-DD format."""
        # Try DD.MM.YYYY format
        match = re.match(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", date_str)
        if match:
            day, month, year = match.groups()
            return f"{year}-{int(month):02d}-{int(day):02d}"
        
        # Try YYYY-MM-DD format
        match = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})", date_str)
        if match:
            year, month, day = match.groups()
            return f"{year}-{int(month):02d}-{int(day):02d}"
        
        return None

    @staticmethod
    def _parse_time(time_str: str) -> Optional[str]:
        """Parse time string to HH:MM format."""
        # Try HH:MM format
        match = re.match(r"(\d{1,2}):(\d{1,2})", time_str)
        if match:
            hour, minute = match.groups()
            hour = int(hour)
            minute = int(minute)
            
            if 0 <= hour < 24 and 0 <= minute < 60:
                return f"{hour:02d}:{minute:02d}"
        
        return None

    @staticmethod
    def _format_date_ru(date_str: str) -> str:
        """Format date as DD.MM.YYYY for display."""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d.%m.%Y")
        except ValueError:
            return date_str

