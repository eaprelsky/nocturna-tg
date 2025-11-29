"""Telegram bot command handlers."""

import logging
from io import BytesIO
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from aiohttp import web
from typing import Optional

from src.services.transit_service import TransitService
from src.services.chart_service import ChartService
from src.services.natal_service import NatalChartService
from src.services.personal_transit_service import PersonalTransitService
from src.api.chart_service_client import ChartServiceError
from src.formatters.russian_formatter import RussianFormatter
from src.database.service import DatabaseService
from src.database.database import get_session


logger = logging.getLogger(__name__)


class BotHandlers:
    """Handles Telegram bot commands and interactions."""

    def __init__(
        self,
        transit_service: TransitService,
        chart_service: Optional[ChartService] = None,
        natal_service: Optional[NatalChartService] = None,
        personal_transit_service: Optional[PersonalTransitService] = None,
    ):
        """
        Initialize bot handlers.

        Args:
            transit_service: Service for transit calculations
            chart_service: Service for chart image generation (optional)
            natal_service: Service for natal chart calculations (optional)
            personal_transit_service: Service for personal transits (optional)
        """
        self.transit_service = transit_service
        self.chart_service = chart_service
        self.natal_service = natal_service
        self.personal_transit_service = personal_transit_service
        self.formatter = RussianFormatter()

    def _split_message(self, text: str, max_length: int = 4000) -> list:
        """
        Split long message into chunks respecting Telegram limits.

        Args:
            text: Message text to split
            max_length: Maximum length per chunk

        Returns:
            List of message chunks
        """
        if len(text) <= max_length:
            return [text]

        # Try to split by double newline (sections)
        sections = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for section in sections:
            if len(current_chunk) + len(section) + 2 <= max_length:
                if current_chunk:
                    current_chunk += "\n\n" + section
                else:
                    current_chunk = section
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = section

                # If single section is too long, split by lines
                if len(section) > max_length:
                    lines = section.split("\n")
                    current_chunk = ""
                    for line in lines:
                        if len(current_chunk) + len(line) + 1 <= max_length:
                            if current_chunk:
                                current_chunk += "\n" + line
                            else:
                                current_chunk = line
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                            current_chunk = line

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /start command.

        Args:
            update: Telegram update object
            context: Telegram context object
        """
        user = update.effective_user
        logger.info(f"User {user.id} started the bot")

        welcome_message = (
            f"Привет, {user.mention_html()}!\n\n"
            "🌟 Я <b>Nocturna Bot</b> — твой астрологический помощник.\n\n"
            "<b>Мои возможности:</b>\n"
            "• Натальные карты и персональные транзиты\n"
            "• Текущие позиции планет\n"
            "• Анализ аспектов между планетами\n"
            "• Транзиты в реальном времени\n"
            "• Визуализация карт\n\n"
            "<b>Доступные команды:</b>\n"
            "/transit - Текущая карта транзитов\n"
            "/natal - Настроить натальную карту\n"
            "/my_natal - Посмотреть свою натальную карту\n"
            "/my_transit - Персональные транзиты\n"
            "/profile - Просмотр сохраненных данных\n"
            "/help - Справка по командам\n\n"
            "Для персональных прогнозов сначала настройте натальную карту: /natal"
        )

        await update.message.reply_text(
            welcome_message, parse_mode=ParseMode.HTML # Change to HTML
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /help command.
        """
        logger.info(f"User {update.effective_user.id} requested help")

        help_message = (
            "📚 <b>Справка по командам</b>\n\n"
            "<b>Персональные команды:</b>\n"
            "/natal - Настроить натальную карту\n"
            "/my_natal - Посмотреть натальную карту\n"
            "/my_transit - Персональные транзиты\n"
            "/profile - Просмотр сохраненных данных\n"
            "/clear_profile - Удалить свои данные\n\n"
            "<b>Общие транзиты:</b>\n"
            "/transit - Текущая карта транзитов\n"
            "/transit_planets - Позиции планет\n"
            "/transit_aspects - Текущие аспекты\n\n"
            "<b>О боте:</b>\n"
            "Бот использует сервер расчетов Nocturna для получения точных "
            "астрологических данных. Все расчеты выполняются в реальном времени.\n\n"
            "<b>Приватность:</b>\n"
            "Мы храним только необходимые данные для астрологических расчетов: "
            "дату, время и место рождения. Вы можете удалить свои данные в любой момент."
        )

        await update.message.reply_text(
            help_message, parse_mode=ParseMode.HTML # Change to HTML
        )

    async def transit_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle /transit command - generate chart image or fallback to text report.
        """
        user_id = update.effective_user.id
        logger.info(f"User {user_id} requested transit chart")

        # Send "calculating" message
        processing_msg = await update.message.reply_text(
            "⏳ Генерирую изображение текущей карты транзитов..."
        )

        try:
            # Try to generate chart image if service is available
            if self.chart_service:
                try:
                    image_bytes = self.chart_service.generate_current_transit_chart()

                    # Send image
                    sent_photo = await update.message.reply_photo(
                        photo=BytesIO(image_bytes),
                        caption="🌟 Текущая карта транзитов"
                    )

                    # Try to get and send interpretation
                    interpretation_raw = self.transit_service.get_interpretation()
                    if interpretation_raw:
                        interpretation_text = f"📖 <b>Интерпретация дня:</b>\n\n{interpretation_raw}"
                        
                        # Max caption length is 1024 characters.
                        # If interpretation is too long, send it as a separate message.
                        if len(interpretation_text) <= 1024 - len("🌟 Текущая карта транзитов"):
                            combined_caption = f"🌟 Текущая карта транзитов\n\n{interpretation_text}"
                            await sent_photo.edit_caption(
                                caption=combined_caption,
                                parse_mode=ParseMode.HTML
                            )
                        else:
                            # Split if too long, and send as separate message
                            if len(interpretation_text) <= 4096:
                                await update.message.reply_text(
                                    interpretation_text, parse_mode=ParseMode.HTML
                                )
                            else:
                                messages = self._split_message(interpretation_text, max_length=4000)
                                for msg in messages:
                                    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

                    await processing_msg.delete() # Delete processing message only if everything is successful
                    return
                except ChartServiceError as e:
                    logger.warning(f"Chart service error, falling back to text: {str(e)}")
                    # Fall through to text report
                except Exception as e:
                    logger.warning(f"Error generating chart image, falling back to text: {str(e)}")
                    # Fall through to text report

            # Fallback to text report if image generation failed or unavailable
            await processing_msg.edit_text("⏳ Рассчитываю текущий транзит планет...")

            # Get transit report
            report = self.transit_service.get_current_transit()
            # Try to get and send interpretation for fallback
            interpretation_raw = self.transit_service.get_interpretation()
            if interpretation_raw:
                report += f"\n\n<b>Интерпретация дня:</b>\n\n{interpretation_raw}" # Use HTML bold tag
            
            # Split long messages (Telegram limit is 4096 characters)
            if len(report) <= 4096:
                await update.message.reply_text(report, parse_mode=ParseMode.HTML)
            else:
                # Split into multiple messages
                messages = self._split_message(report, max_length=4000)
                for msg in messages:
                    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
                
                await processing_msg.delete() # Delete processing message only if everything is successful

        except Exception as e:
            logger.error(f"Error processing transit command: {str(e)}", exc_info=True)
            await processing_msg.edit_text(
                f"❌ Произошла ошибка при расчете транзита.\n\n"
                f"Детали: {str(e)}\n\n"
                f"Пожалуйста, попробуйте позже или обратитесь к администратору."
            )

    async def transit_planets_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle /transit_planets command - show planetary positions.
        """
        user_id = update.effective_user.id
        logger.info(f"User {user_id} requested transit planets")

        # Send "calculating" message
        processing_msg = await update.message.reply_text(
            "⏳ Рассчитываю текущие позиции планет..."
        )

        try:
            # Get positions
            positions = self.transit_service.get_current_positions()

            # Format positions
            positions_text = self.formatter.format_positions_list(positions)

            # Send message
            await update.message.reply_text(positions_text, parse_mode=ParseMode.HTML)
            
            await processing_msg.delete() # Delete processing message only if everything is successful

        except Exception as e:
            logger.error(f"Error processing transit_planets command: {str(e)}", exc_info=True)
            await processing_msg.edit_text(
                f"❌ Произошла ошибка при расчете позиций планет.\n\n"
                f"Детали: {str(e)}\n\n"
                f"Пожалуйста, попробуйте позже или обратитесь к администратору."
            )

    async def transit_aspects_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle /transit_aspects command - show planetary aspects.
        """
        user_id = update.effective_user.id
        logger.info(f"User {user_id} requested transit aspects")

        # Send "calculating" message
        processing_msg = await update.message.reply_text(
            "⏳ Рассчитываю текущие аспекты..."
        )

        try:
            # Get aspects
            aspects = self.transit_service.get_current_aspects()

            # Format aspects
            aspects_text = self.formatter.format_aspects_list(aspects)

            # Send message
            await update.message.reply_text(aspects_text, parse_mode=ParseMode.HTML)
            
            await processing_msg.delete() # Delete processing message only if everything is successful

        except Exception as e:
            logger.error(f"Error processing transit_aspects command: {str(e)}", exc_info=True)
            await processing_msg.edit_text(
                f"❌ Произошла ошибка при расчете аспектов.\n\n"
                f"Детали: {str(e)}\n\n"
                f"Пожалуйста, попробуйте позже или обратитесь к администратору."
            )

    async def my_natal_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle /my_natal command - show user's natal chart with image and interpretation.
        """
        user_id = update.effective_user.id
        logger.info(f"User {user_id} requested their natal chart")

        processing_msg = await update.message.reply_text(
            "⏳ Генерирую изображение вашей натальной карты..."
        )

        try:
            if not self.natal_service:
                await processing_msg.edit_text(
                    "❌ Сервис натальных карт недоступен.\n\n"
                    "Пожалуйста, обратитесь к администратору."
                )
                return

            # Get user's birth data from database
            birth_data = None
            async for session in get_session():
                db_service = DatabaseService(session)
                birth_data = await db_service.get_birth_data(user_id)
                break

            if not birth_data:
                await processing_msg.edit_text(
                    "❌ У вас еще не настроена натальная карта.\n\n"
                    "Используйте /natal для настройки."
                )
                return

            # Use cached chart data (required since API doesn't persist charts)
            if not birth_data.natal_chart_cache:
                await processing_msg.edit_text(
                    "❌ Данные натальной карты недоступны.\n\n"
                    "Пожалуйста, настройте карту заново: /natal"
                )
                return
            
            logger.info(f"Using cached chart data for user {user_id}")
            chart_data = birth_data.natal_chart_cache
            positions = chart_data.get("positions", [])
            houses = chart_data.get("houses", [])

            # Try to generate chart image if service is available
            if self.chart_service:
                try:
                    image_bytes = self.chart_service.generate_natal_chart(
                        positions=positions,
                        houses=houses,
                    )

                    # Prepare basic caption with birth info
                    caption = (
                        f"🌟 Натальная карта\n"
                        f"📅 {birth_data.birth_date} 🕐 {birth_data.birth_time}"
                    )

                    # Send image
                    sent_photo = await update.message.reply_photo(
                        photo=BytesIO(image_bytes),
                        caption=caption
                    )

                    # Try to get and send interpretation
                    if self.natal_service.interpretation_service:
                        try:
                            logger.info("Generating LLM interpretation for natal chart...")
                            interpretation = self.natal_service.interpretation_service.interpret_natal_chart(
                                positions=positions,
                                houses=houses,
                            )
                            
                            if interpretation:
                                interpretation_text = f"📖 <b>Интерпретация натальной карты:</b>\n\n{interpretation}"
                                
                                # Send interpretation as separate message
                                if len(interpretation_text) <= 4096:
                                    await update.message.reply_text(
                                        interpretation_text, parse_mode=ParseMode.HTML
                                    )
                                else:
                                    messages = self._split_message(interpretation_text, max_length=4000)
                                    for msg in messages:
                                        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
                        except Exception as e:
                            logger.warning(f"Error generating interpretation: {str(e)}")
                            # Continue without interpretation

                    await processing_msg.delete()
                    return

                except ChartServiceError as e:
                    logger.warning(f"Chart service error, falling back to text: {str(e)}")
                    # Fall through to text report
                except Exception as e:
                    logger.warning(f"Error generating chart image, falling back to text: {str(e)}")
                    # Fall through to text report

            # Fallback to text report if image generation failed or unavailable
            await processing_msg.edit_text("⏳ Формирую текстовый отчет...")

            # Format natal chart report
            report = self.natal_service.format_natal_chart_report(
                positions=positions,
                houses=houses,
                birth_date=birth_data.birth_date,
                birth_time=birth_data.birth_time,
            )

            # Try to add interpretation to text report
            if self.natal_service.interpretation_service:
                try:
                    logger.info("Generating LLM interpretation for natal chart...")
                    interpretation = self.natal_service.interpretation_service.interpret_natal_chart(
                        positions=positions,
                        houses=houses,
                    )
                    if interpretation:
                        report += f"\n\n<b>Интерпретация натальной карты:</b>\n\n{interpretation}"
                except Exception as e:
                    logger.warning(f"Error generating interpretation: {str(e)}")

            # Send report
            if len(report) <= 4096:
                await update.message.reply_text(report, parse_mode=ParseMode.HTML)
            else:
                messages = self._split_message(report, max_length=4000)
                for msg in messages:
                    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

            await processing_msg.delete()

        except Exception as e:
            logger.error(f"Error processing my_natal command: {str(e)}", exc_info=True)
            await processing_msg.edit_text(
                f"❌ Произошла ошибка при получении натальной карты.\n\n"
                f"Детали: {str(e)}\n\n"
                f"Пожалуйста, попробуйте позже или обратитесь к администратору."
            )

    async def my_transit_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle /my_transit command - show user's personal transits with chart and interpretation.
        """
        user_id = update.effective_user.id
        logger.info(f"User {user_id} requested their personal transits")

        processing_msg = await update.message.reply_text(
            "⏳ Рассчитываю персональные транзиты..."
        )

        try:
            if not self.personal_transit_service:
                await processing_msg.edit_text(
                    "❌ Сервис персональных транзитов недоступен.\n\n"
                    "Пожалуйста, обратитесь к администратору."
                )
                return

            # Get user's birth data from database
            birth_data = None
            async for session in get_session():
                db_service = DatabaseService(session)
                birth_data = await db_service.get_birth_data(user_id)
                break

            if not birth_data:
                await processing_msg.edit_text(
                    "❌ У вас еще не настроена натальная карта.\n\n"
                    "Используйте /natal для настройки."
                )
                return

            # Calculate personal transits
            transit_data = await self.personal_transit_service.calculate_personal_transits(
                natal_chart_id=birth_data.chart_id or "cached",
                latitude=birth_data.latitude,
                longitude=birth_data.longitude,
                timezone=birth_data.timezone,
                natal_birth_date=birth_data.birth_date,
                natal_birth_time=birth_data.birth_time,
                natal_latitude=birth_data.latitude,
                natal_longitude=birth_data.longitude,
                natal_timezone=birth_data.timezone,
            )

            transit_positions = transit_data.get("transit_positions", [])
            transit_houses = transit_data.get("transit_houses", [])
            natal_positions = transit_data.get("natal_positions", [])
            natal_houses = transit_data.get("natal_houses", [])
            transit_aspects = transit_data.get("transit_aspects", [])
            transit_date = transit_data.get("transit_date", "N/A")
            transit_time = transit_data.get("transit_time", "N/A")

            # Debug logging
            logger.info(f"Chart service available: {self.chart_service is not None}")
            logger.info(f"Natal positions count: {len(natal_positions) if natal_positions else 0}")
            logger.info(f"Natal houses count: {len(natal_houses) if natal_houses else 0}")
            logger.info(f"Transit positions count: {len(transit_positions) if transit_positions else 0}")

            # Try to generate biwheel chart if service is available
            if self.chart_service and natal_positions and natal_houses and transit_positions:
                try:
                    await processing_msg.edit_text("⏳ Генерирую биколесную карту транзитов...")
                    
                    image_bytes = self.chart_service.generate_personal_transit_chart(
                        natal_positions=natal_positions,
                        natal_houses=natal_houses,
                        transit_positions=transit_positions,
                        transit_date=transit_date,
                        transit_time=transit_time,
                    )

                    # Prepare caption with basic info
                    caption = (
                        f"🌟 Персональные транзиты\n"
                        f"📅 {transit_date} 🕐 {transit_time}"
                    )

                    # Send image
                    sent_photo = await update.message.reply_photo(
                        photo=BytesIO(image_bytes),
                        caption=caption
                    )

                    # Try to get and send interpretation
                    if self.personal_transit_service.interpretation_service and natal_positions and transit_aspects:
                        try:
                            logger.info("Generating LLM interpretation for personal transits...")
                            interpretation = self.personal_transit_service.interpretation_service.interpret_personal_transits(
                                natal_positions=natal_positions,
                                transit_aspects=transit_aspects,
                            )
                            
                            if interpretation:
                                interpretation_text = f"📖 <b>Интерпретация персональных транзитов:</b>\n\n{interpretation}"
                                
                                # Send interpretation as separate message
                                if len(interpretation_text) <= 4096:
                                    await update.message.reply_text(
                                        interpretation_text, parse_mode=ParseMode.HTML
                                    )
                                else:
                                    messages = self._split_message(interpretation_text, max_length=4000)
                                    for msg in messages:
                                        await update.message.reply_text(msg, parse_mode=ParseMode.HTML)
                        except Exception as e:
                            logger.warning(f"Error generating interpretation: {str(e)}")
                            # Continue without interpretation

                    await processing_msg.delete()
                    return

                except ChartServiceError as e:
                    logger.warning(f"Chart service error, falling back to text: {str(e)}")
                    # Fall through to text report
                except Exception as e:
                    logger.warning(f"Error generating chart image, falling back to text: {str(e)}")
                    # Fall through to text report

            # Fallback to text report if image generation failed or unavailable
            await processing_msg.edit_text("⏳ Формирую текстовый отчет...")

            # Format transit report
            report = self.personal_transit_service.format_personal_transit_report(transit_data)

            # Try to add interpretation to text report
            if self.personal_transit_service.interpretation_service and natal_positions and transit_aspects:
                try:
                    logger.info("Generating LLM interpretation for personal transits...")
                    interpretation = self.personal_transit_service.interpretation_service.interpret_personal_transits(
                        natal_positions=natal_positions,
                        transit_aspects=transit_aspects,
                    )
                    if interpretation:
                        report += f"\n\n<b>📖 Интерпретация персональных транзитов:</b>\n\n{interpretation}"
                except Exception as e:
                    logger.warning(f"Error generating interpretation: {str(e)}")

            # Send report
            if len(report) <= 4096:
                await update.message.reply_text(report, parse_mode=ParseMode.HTML)
            else:
                messages = self._split_message(report, max_length=4000)
                for msg in messages:
                    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

            await processing_msg.delete()

        except Exception as e:
            logger.error(f"Error processing my_transit command: {str(e)}", exc_info=True)
            await processing_msg.edit_text(
                f"❌ Произошла ошибка при расчете персональных транзитов.\n\n"
                f"Детали: {str(e)}\n\n"
                f"Пожалуйста, попробуйте позже или обратитесь к администратору."
            )

    async def profile_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle /profile command - show user's saved data.
        """
        user_id = update.effective_user.id
        logger.info(f"User {user_id} requested their profile")

        try:
            async for session in get_session():
                db_service = DatabaseService(session)
                birth_data = await db_service.get_birth_data(user_id)

            if not birth_data:
                await update.message.reply_text(
                    "❌ У вас еще нет сохраненных данных.\n\n"
                    "Используйте /natal для настройки натальной карты."
                )
                return

            # Format profile info
            message = (
                "👤 <b>Ваш профиль</b>\n\n"
                f"📅 <b>Дата рождения:</b> {birth_data.birth_date}\n"
                f"🕐 <b>Время рождения:</b> {birth_data.birth_time}\n"
                f"📍 <b>Место рождения:</b> {birth_data.location_name or 'Не указано'}\n"
                f"🌍 <b>Координаты:</b> {birth_data.latitude:.4f}, {birth_data.longitude:.4f}\n"
                f"🕰 <b>Часовой пояс:</b> {birth_data.timezone}\n"
                f"🆔 <b>Chart ID:</b> {birth_data.chart_id or 'Не создан'}\n\n"
                "💡 Используйте /clear_profile для удаления данных"
            )

            await update.message.reply_text(message, parse_mode=ParseMode.HTML)

        except Exception as e:
            logger.error(f"Error processing profile command: {str(e)}", exc_info=True)
            await update.message.reply_text(
                "❌ Ошибка при получении профиля.\n\n"
                "Пожалуйста, попробуйте позже."
            )

    async def clear_profile_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle /clear_profile command - delete user's data.
        """
        user_id = update.effective_user.id
        logger.info(f"User {user_id} requested to clear their profile")

        try:
            async for session in get_session():
                db_service = DatabaseService(session)
                birth_data = await db_service.get_birth_data(user_id)

                if not birth_data:
                    await update.message.reply_text(
                        "ℹ️ У вас нет сохраненных данных для удаления."
                    )
                    return

                # Delete chart from API if exists
                if birth_data.chart_id:
                    try:
                        # We should use nocturna_client here, but we don't have access to it
                        # from handlers. This is a design issue we can fix later.
                        logger.info(f"Chart {birth_data.chart_id} should be deleted from API")
                    except Exception as e:
                        logger.warning(f"Failed to delete chart from API: {str(e)}")

                # Delete birth data from database
                deleted = await db_service.delete_birth_data(user_id)

            if deleted:
                await update.message.reply_text(
                    "✅ <b>Ваши данные удалены</b>\n\n"
                    "Вы можете настроить новую натальную карту с помощью /natal",
                    parse_mode=ParseMode.HTML
                )
            else:
                await update.message.reply_text(
                    "❌ Не удалось удалить данные.\n\n"
                    "Пожалуйста, попробуйте позже."
                )

        except Exception as e:
            logger.error(f"Error processing clear_profile command: {str(e)}", exc_info=True)
            await update.message.reply_text(
                "❌ Ошибка при удалении данных.\n\n"
                "Пожалуйста, попробуйте позже."
            )

    async def error_handler(
        self, update: object, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle errors in the bot.

        Args:
            update: Telegram update object
            context: Telegram context object
        """
        logger.error(f"Exception while handling an update: {context.error}")

        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка при обработке команды.\n"
                "Пожалуйста, попробуйте позже."
            )

    @staticmethod
    async def health_check(request: web.Request) -> web.Response:
        """
        Health check endpoint for monitoring.

        Args:
            request: aiohttp request object

        Returns:
            JSON response with health status
        """
        return web.json_response({
            "status": "healthy",
            "service": "nocturna-telegram-bot"
        })

