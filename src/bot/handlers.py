"""Telegram bot command handlers."""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from src.services.transit_service import TransitService


logger = logging.getLogger(__name__)


class BotHandlers:
    """Handles Telegram bot commands and interactions."""

    def __init__(self, transit_service: TransitService):
        """
        Initialize bot handlers.

        Args:
            transit_service: Service for transit calculations
        """
        self.transit_service = transit_service

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
            f"Привет, {user.mention_markdown_v2()}\\!\n\n"
            "🌟 Я *Nocturna Bot* — твой астрологический помощник\\.\n\n"
            "*Мои возможности:*\n"
            "• Текущие позиции планет\n"
            "• Анализ аспектов между планетами\n"
            "• Транзиты в реальном времени\n\n"
            "*Доступные команды:*\n"
            "/transit \\- Получить текущий транзит планет\n"
            "/help \\- Справка по командам\n\n"
            "Нажми /transit, чтобы начать\\!"
        )

        await update.message.reply_text(
            welcome_message, parse_mode=ParseMode.MARKDOWN_V2
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /help command.

        Args:
            update: Telegram update object
            context: Telegram context object
        """
        logger.info(f"User {update.effective_user.id} requested help")

        help_message = (
            "📚 *Справка по командам*\n\n"
            "*Основные команды:*\n"
            "/transit \\- Текущие позиции планет и аспекты\n"
            "/help \\- Показать эту справку\n\n"
            "*О боте:*\n"
            "Бот использует сервер расчетов Nocturna для получения точных "
            "астрологических данных\\. Все расчеты выполняются в реальном времени\\.\n\n"
            "*Технические детали:*\n"
            "• Координаты: Москва \\(55\\.7558°N, 37\\.6173°E\\)\n"
            "• Часовой пояс: Europe/Moscow\n"
            "• Система домов: Placidus\n"
        )

        await update.message.reply_text(
            help_message, parse_mode=ParseMode.MARKDOWN_V2
        )

    async def transit_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handle /transit command.

        Args:
            update: Telegram update object
            context: Telegram context object
        """
        user_id = update.effective_user.id
        logger.info(f"User {user_id} requested transit")

        # Send "calculating" message
        processing_msg = await update.message.reply_text(
            "⏳ Рассчитываю текущий транзит планет..."
        )

        try:
            # Get transit report
            report = self.transit_service.get_current_transit()

            # Delete processing message
            await processing_msg.delete()

            # Split long messages (Telegram limit is 4096 characters)
            if len(report) <= 4096:
                await update.message.reply_text(report, parse_mode=ParseMode.MARKDOWN)
            else:
                # Split into multiple messages
                messages = self._split_message(report, max_length=4000)
                for msg in messages:
                    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            logger.error(f"Error processing transit command: {str(e)}", exc_info=True)
            await processing_msg.edit_text(
                f"❌ Произошла ошибка при расчете транзита.\n\n"
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

