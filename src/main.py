"""Main entry point for Nocturna Telegram Bot."""

import logging
import sys
import jwt
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler

from src.config import get_settings
from src.api.nocturna_client import NocturnaClient
from src.api.openrouter_client import OpenRouterClient
from src.api.chart_service_client import ChartServiceClient
from src.services.transit_service import TransitService
from src.services.interpretation_service import InterpretationService
from src.services.chart_service import ChartService
from src.bot.handlers import BotHandlers


# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


def check_token_expiry(token: str) -> None:
    """
    Check service token expiration and warn if expiring soon.

    Args:
        token: JWT service token

    Raises:
        SystemExit: If token is expired
    """
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        exp_timestamp = payload.get("exp")
        
        if not exp_timestamp:
            logger.warning("Could not determine token expiration")
            return
        
        exp_date = datetime.fromtimestamp(exp_timestamp)
        days_left = (exp_date - datetime.now()).days
        
        if days_left <= 0:
            logger.error("Service token has expired")
            logger.error("Generate new token: cd nocturna-calculations && make service-token-create")
            sys.exit(1)
        elif days_left <= 7:
            logger.warning(f"Service token expires in {days_left} days")
            logger.warning("Consider refreshing token soon")
        else:
            logger.info(f"Service token valid for {days_left} days")
            
    except jwt.DecodeError:
        logger.warning("Could not decode service token")
    except Exception as e:
        logger.warning(f"Token validation error: {e}")


def main() -> None:
    """
    Main function to run the bot.

    Initializes all components and starts the bot polling.
    """
    try:
        # Load configuration
        logger.info("Loading configuration...")
        settings = get_settings()

        # Set logging level based on settings
        logging.getLogger().setLevel(settings.log_level.upper())

        # Check service token expiration
        if settings.nocturna_service_token:
            check_token_expiry(settings.nocturna_service_token)

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

        # Initialize Chart Service client (optional)
        chart_service = None
        if settings.chart_service_api_key and settings.chart_service_api_key.strip():
            logger.info(f"Initializing Chart Service client: {settings.chart_service_url}")
            logger.debug(f"Chart Service API key length: {len(settings.chart_service_api_key)}")
            chart_service_client = ChartServiceClient(
                base_url=settings.chart_service_url,
                api_key=settings.chart_service_api_key,
                timeout=settings.chart_service_timeout,
            )
            chart_service = ChartService(
                nocturna_client=nocturna_client,
                chart_service_client=chart_service_client,
                timezone=settings.timezone,
            )
        else:
            logger.warning("Chart Service API key not found or empty. Chart image generation disabled.")
            logger.debug(f"chart_service_api_key value: {repr(settings.chart_service_api_key)}")

        # Initialize services
        logger.info("Initializing services...")
        transit_service = TransitService(
            nocturna_client=nocturna_client,
            timezone=settings.timezone,
            interpretation_service=interpretation_service,
        )

        # Initialize bot handlers
        logger.info("Initializing bot handlers...")
        handlers = BotHandlers(
            transit_service=transit_service,
            chart_service=chart_service,
        )

        # Create application
        logger.info("Creating Telegram application...")
        application = Application.builder().token(settings.telegram_bot_token).build()

        # Register command handlers
        application.add_handler(CommandHandler("start", handlers.start_command))
        application.add_handler(CommandHandler("help", handlers.help_command))
        application.add_handler(CommandHandler("transit", handlers.transit_command))
        application.add_handler(CommandHandler("transit_planets", handlers.transit_planets_command))
        application.add_handler(CommandHandler("transit_aspects", handlers.transit_aspects_command))

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

