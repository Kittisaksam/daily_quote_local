"""PythonAnywhere compatible runner for Daily Quote Bot.

This script is designed to run on PythonAnywhere using:
1. Always-on task (for the bot listener)
2. Scheduled task (for daily quotes)

For more info: https://help.pythonanywhere.com/
"""
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('/var/www/daily_quote_pythonanywhere_com/log.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_scheduled():
    """Run scheduled quote sending (for PythonAnywhere Scheduled Task).

    This function sends quotes immediately and exits.
    Use this with PythonAnywhere's scheduled tasks.
    """
    logger.info("=" * 50)
    logger.info("Running scheduled quote task")
    logger.info("=" * 50)

    from bot.scheduler import get_scheduler
    from config.settings import load_config

    try:
        # Load configuration
        config = load_config()
        logger.info(f"Configuration loaded: {config.schedule_window}")

        # Create scheduler instance
        scheduler = get_scheduler()

        # Send morning quote
        if config.schedule_window in ['morning', 'both']:
            logger.info("Sending morning quote...")
            scheduler.send_daily_quote('morning')

        # Send evening quote
        if config.schedule_window in ['evening', 'both']:
            logger.info("Sending evening quote...")
            scheduler.send_daily_quote('evening')

        logger.info("Scheduled task completed successfully")

    except Exception as e:
        logger.error(f"Error in scheduled task: {e}", exc_info=True)
        sys.exit(1)


def run_bot():
    """Run Telegram bot (for PythonAnywhere Always-on Task).

    This keeps the bot running 24/7 to respond to commands.
    Use this with PythonAnywhere's always-on tasks.
    """
    logger.info("=" * 50)
    logger.info("Starting Telegram bot on PythonAnywhere")
    logger.info("=" * 50)

    from bot.telegram_bot import run_bot

    try:
        run_bot()
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Check command line argument
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "scheduled":
            run_scheduled()
        elif mode == "bot":
            run_bot()
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python pythonanywhere_run.py [scheduled|bot]")
            sys.exit(1)
    else:
        print("Please specify mode:")
        print("  python pythonanywhere_run.py scheduled  - Send quotes and exit")
        print("  python pythonanywhere_run.py bot         - Run bot listener")
        sys.exit(1)
