"""Telegram bot command handlers."""

import logging
from io import BytesIO
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.services.transit_service import TransitService
from src.services.chart_service import ChartService
from src.api.chart_service_client import ChartServiceError
from src.formatters.russian_formatter import RussianFormatter
from typing import Optional


logger = logging.getLogger(__name__)


class BotHandlers:
    """Handles Telegram bot commands and interactions."""

    def __init__(self, transit_service: TransitService, chart_service: Optional[ChartService] = None):
        """
        Initialize bot handlers.

        Args:
            transit_service: Service for transit calculations
            chart_service: Service for chart image generation (optional)
        """
        self.transit_service = transit_service
        self.chart_service = chart_service
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
            f"Привет, {user.mention_html()}\!\n\n" # Use mention_html
            "🌟 Я <b>Nocturna Bot</b> — твой астрологический помощник.\n\n" # Use HTML bold tag
            "<b>Мои возможности:</b>\n" # Use HTML bold tag
            "• Текущие позиции планет\n"
            "• Анализ аспектов между планетами\n"
            "• Транзиты в реальном времени\n"
            "• Визуализация карт\n\n"
            "<b>Доступные команды:</b>\n" # Use HTML bold tag
            "/transit \- Изображение текущей карты транзитов\n"
            "/transit_planets \- Список текущих позиций планет\n"
            "/transit_aspects \- Список текущих аспектов\n"
            "/help \- Справка по командам\n\n"
            "Нажми /transit, чтобы начать!"
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
            "📚 <b>Справка по командам</b>\n\n" # Use HTML bold tag
            "<b>Основные команды:</b>\n" # Use HTML bold tag
            "/transit \- Изображение текущей карты транзитов\n"
            "/transit_planets \- Текстовый список текущих позиций планет\n"
            "/transit_aspects \- Текстовый список текущих аспектов\n"
            "/help \- Показать эту справку\n\n"
            "<b>О боте:</b>\n" # Use HTML bold tag
            "Бот использует сервер расчетов Nocturna для получения точных "
            "астрологических данных. Все расчеты выполняются в реальном времени.\n\n"
            "<b>Технические детали:</b>\n" # Use HTML bold tag
            "• Координаты: Москва (55.7558°N, 37.6173°E)\n"
            "• Часовой пояс: Europe/Moscow\n"
            "• Система домов: Placidus\n"
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

