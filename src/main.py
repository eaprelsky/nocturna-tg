"""Main entry point for Nocturna Telegram Bot."""

import asyncio
import logging
import sys
import jwt
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler
from aiohttp import web

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


async def run_polling(application: Application, settings) -> None:
    """
    Run bot in polling mode (for local development).

    Args:
        application: Telegram application instance
        settings: Application settings
    """
    logger.info("Starting bot in POLLING mode...")
    logger.info(f"Bot username: {settings.telegram_bot_username or 'Not set'}")
    logger.info("Bot is running. Press Ctrl+C to stop.")

    await application.initialize()
    await application.start()
    await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

    # Keep the bot running
    try:
        import asyncio
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping bot...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


async def run_webhook(application: Application, settings, handlers: BotHandlers) -> None:
    """
    Run bot in webhook mode (for production).

    Args:
        application: Telegram application instance
        settings: Application settings
        handlers: Bot handlers instance
    """
    logger.info("Starting bot in WEBHOOK mode...")
    logger.info(f"Webhook URL: {settings.webhook_url}{settings.webhook_path}")
    logger.info(f"Listening on {settings.webhook_host}:{settings.webhook_port}")
    logger.info(f"Bot username: {settings.telegram_bot_username or 'Not set'}")

    # Create aiohttp application for webhook
    aiohttp_app = web.Application()
    
    # Add health check endpoint
    aiohttp_app.router.add_get("/health", handlers.health_check)
    
    # Initialize and start bot
    await application.initialize()
    await application.start()
    
    # Set webhook
    webhook_url = f"{settings.webhook_url}{settings.webhook_path}"
    await application.bot.set_webhook(
        url=webhook_url,
        allowed_updates=Update.ALL_TYPES,
        secret_token=settings.webhook_secret,
    )
    
    # Configure webhook handler
    async def telegram_webhook(request: web.Request) -> web.Response:
        """Handle incoming webhook requests from Telegram."""
        try:
            # Verify secret token if configured
            if settings.webhook_secret:
                token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
                if token != settings.webhook_secret:
                    logger.warning("Invalid webhook secret token")
                    return web.Response(status=403)
            
            # Process update asynchronously without waiting
            # This prevents 504 Gateway Timeout when processing takes long
            update_data = await request.json()
            update = Update.de_json(update_data, application.bot)
            
            # Process update in background task
            asyncio.create_task(application.process_update(update))
            
            # Immediately return 200 OK to Telegram
            return web.Response(status=200)
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return web.Response(status=500)
    
    # Add webhook endpoint
    aiohttp_app.router.add_post(settings.webhook_path, telegram_webhook)
    
    # Run aiohttp server
    runner = web.AppRunner(aiohttp_app)
    await runner.setup()
    site = web.TCPSite(runner, settings.webhook_host, settings.webhook_port)
    
    try:
        await site.start()
        logger.info("Webhook server started successfully")
        
        # Keep the server running
        import asyncio
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping webhook server...")
    finally:
        await application.stop()
        await application.shutdown()
        await runner.cleanup()


def main() -> None:
    """
    Main function to run the bot.

    Initializes all components and starts the bot in polling or webhook mode.
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

        # Start the bot in the appropriate mode
        import asyncio
        if settings.bot_mode == "webhook":
            asyncio.run(run_webhook(application, settings, handlers))
        else:
            asyncio.run(run_polling(application, settings))

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

