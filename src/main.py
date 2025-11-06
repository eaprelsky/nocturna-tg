"""Main entry point for Nocturna Telegram Bot."""

import logging
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler

from src.config import get_settings
from src.api.nocturna_client import NocturnaClient
from src.api.openrouter_client import OpenRouterClient
from src.services.transit_service import TransitService
from src.services.interpretation_service import InterpretationService
from src.bot.handlers import BotHandlers


# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


def main() -> None:
    """
    Main function to run the bot.

    Initializes all components and starts the bot polling.
    """
    try:
        # Load configuration
        logger.info("Loading configuration...")
        settings = get_settings()

        # Initialize Nocturna API client
        logger.info(f"Initializing Nocturna API client: {settings.nocturna_api_url}")
        nocturna_client = NocturnaClient(
            api_url=settings.nocturna_api_url,
            service_token=settings.nocturna_service_token,
            timeout=settings.nocturna_timeout,
            max_retries=settings.nocturna_max_retries,
        )

        # Initialize OpenRouter client (optional)
        interpretation_service = None
        if settings.openrouter_api_key:
            logger.info(f"Initializing OpenRouter client: {settings.openrouter_model}")
            openrouter_client = OpenRouterClient(
                api_key=settings.openrouter_api_key, model=settings.openrouter_model
            )
            interpretation_service = InterpretationService(openrouter_client)
        else:
            logger.warning("OpenRouter API key not found. Interpretation disabled.")

        # Initialize services
        logger.info("Initializing services...")
        transit_service = TransitService(
            nocturna_client=nocturna_client,
            timezone=settings.timezone,
            interpretation_service=interpretation_service,
        )

        # Initialize bot handlers
        logger.info("Initializing bot handlers...")
        handlers = BotHandlers(transit_service=transit_service)

        # Create application
        logger.info("Creating Telegram application...")
        application = Application.builder().token(settings.telegram_bot_token).build()

        # Register command handlers
        application.add_handler(CommandHandler("start", handlers.start_command))
        application.add_handler(CommandHandler("help", handlers.help_command))
        application.add_handler(CommandHandler("transit", handlers.transit_command))

        # Register error handler
        application.add_error_handler(handlers.error_handler)

        # Start the bot
        logger.info("Starting bot polling...")
        logger.info(f"Bot username: {settings.telegram_bot_username or 'Not set'}")
        logger.info("Bot is running. Press Ctrl+C to stop.")

        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

