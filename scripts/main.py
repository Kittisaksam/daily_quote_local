"""Main entry point for the Daily Quote Bot.

This script starts both the Telegram bot and the scheduler.
"""
import logging
import signal
import sys
from typing import Optional

from bot.telegram_bot import run_bot
from bot.scheduler import get_scheduler, QuoteScheduler
from config.settings import load_config, Config

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

# Global scheduler reference for shutdown
_scheduler: Optional[QuoteScheduler] = None


def setup_signal_handlers(scheduler: QuoteScheduler):
    """Setup signal handlers for graceful shutdown.

    Args:
        scheduler: The scheduler instance to shutdown on signal
    """
    def shutdown_handler(signum, frame):
        logger.info("Shutting down gracefully...")
        scheduler.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)


def log_scheduled_jobs(scheduler: QuoteScheduler):
    """Log the scheduled jobs information.

    Args:
        scheduler: The scheduler instance
    """
    jobs = scheduler.list_jobs()
    logger.info(f"Scheduled {len(jobs)} job(s):")
    for job in jobs:
        logger.info(f"  - {job['name']}: {job['next_run_time']}")


def main():
    """Main function to run the bot with scheduler."""
    logger.info("=" * 50)
    logger.info("Starting Daily Quote Bot")
    logger.info("=" * 50)

    try:
        # Load configuration
        config: Config = load_config()
        logger.info(f"Configuration loaded successfully")
        logger.info(f"  Schedule window: {config.schedule_window}")
        logger.info(f"  Quote language: {config.quote_language}")

        # Setup scheduler
        logger.info("Setting up scheduler...")
        global _scheduler
        _scheduler = get_scheduler()
        log_scheduled_jobs(_scheduler)

        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(_scheduler)

        logger.info("-" * 50)
        logger.info("Bot is now running!")
        logger.info("Press Ctrl+C to stop")
        logger.info("-" * 50)

        # Run the Telegram bot (blocking)
        run_bot()

    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
