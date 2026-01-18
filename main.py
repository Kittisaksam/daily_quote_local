"""Main entry point for the Daily Quote Bot.

This script starts both the Telegram bot and the scheduler.
"""
import logging
import signal
import sys
from bot.telegram_bot import run_bot
from bot.scheduler import get_scheduler
from config.settings import load_config

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('daily_quote.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run the bot with scheduler."""
    logger.info("=" * 50)
    logger.info("Starting Daily Quote Bot")
    logger.info("=" * 50)

    try:
        # Load configuration
        config = load_config()
        logger.info(f"Configuration loaded successfully")
        logger.info(f"Schedule window: {config.schedule_window}")
        logger.info(f"Quote language: {config.quote_language}")

        # Setup scheduler
        logger.info("Setting up scheduler...")
        scheduler = get_scheduler()

        # Show scheduled jobs
        jobs = scheduler.list_jobs()
        logger.info(f"Scheduled {len(jobs)} job(s):")
        for job in jobs:
            logger.info(f"  - {job['name']}: {job['next_run_time']}")

        logger.info("-" * 50)
        logger.info("Bot is now running!")
        logger.info("Press Ctrl+C to stop")
        logger.info("-" * 50)

        # Setup signal handler for graceful shutdown
        def signal_handler(sig, frame):
            logger.info("Shutting down gracefully...")
            scheduler.shutdown()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Run the Telegram bot (blocking)
        run_bot()

    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
