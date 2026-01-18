"""Scheduler module for sending daily quotes at scheduled times."""
import random
import logging
from datetime import datetime, time
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
from config.settings import config
from bot.quote_generator import get_quote
from bot.telegram_bot import send_quote_sync

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class QuoteScheduler:
    """Scheduler for sending daily quotes."""

    def __init__(self):
        """Initialize the scheduler."""
        # Persistent job store
        job_stores = {
            'default': SQLAlchemyJobStore(url=f'sqlite:///{config.stats_file.parent}/scheduler.sqlite')
        }

        self.scheduler = BackgroundScheduler(
            jobstores=job_stores,
            timezone='Asia/Bangkok'  # Can be made configurable
        )
        self.scheduler.start()

    def parse_time(self, time_str: str) -> time:
        """Parse time string (HH:MM) to time object.

        Args:
            time_str: Time string in HH:MM format

        Returns:
            datetime.time object
        """
        hour, minute = map(int, time_str.split(':'))
        return time(hour=hour, minute=minute)

    def get_random_time_in_window(self, start_str: str, end_str: str) -> time:
        """Get a random time within a time window.

        Args:
            start_str: Start time in HH:MM format
            end_str: End time in HH:MM format

        Returns:
            datetime.time object with random time
        """
        start_time = self.parse_time(start_str)
        end_time = self.parse_time(end_str)

        # Convert to minutes since midnight
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute

        # Get random minute in range
        random_minutes = random.randint(start_minutes, end_minutes)

        # Convert back to time
        random_hour = random_minutes // 60
        random_minute = random_minutes % 60

        return time(hour=random_hour, minute=random_minute)

    def send_daily_quote(self, time_period: str = "unknown"):
        """Send a daily quote.

        Args:
            time_period: 'morning' or 'evening'
        """
        logger.info(f"Sending scheduled {time_period} quote...")

        # Get quote
        quote = get_quote(language=config.quote_language)

        # Send to Telegram
        success = send_quote_sync(quote, time_period=time_period)

        if success:
            logger.info(f"Successfully sent {time_period} quote")
        else:
            logger.error(f"Failed to send {time_period} quote")

    def schedule_morning_quote(self):
        """Schedule a daily quote in the morning window."""
        # Get random time in morning window
        random_time = self.get_random_time_in_window(
            config.morning_start,
            config.morning_end
        )

        logger.info(f"Scheduling morning quote at {random_time}")

        # Add job
        self.scheduler.add_job(
            self.send_daily_quote,
            trigger=CronTrigger(
                hour=random_time.hour,
                minute=random_time.minute
            ),
            args=['morning'],
            id='morning_quote',
            name='Morning Quote',
            replace_existing=True
        )

    def schedule_evening_quote(self):
        """Schedule a daily quote in the evening window."""
        # Get random time in evening window
        random_time = self.get_random_time_in_window(
            config.evening_start,
            config.evening_end
        )

        logger.info(f"Scheduling evening quote at {random_time}")

        # Add job
        self.scheduler.add_job(
            self.send_daily_quote,
            trigger=CronTrigger(
                hour=random_time.hour,
                minute=random_time.minute
            ),
            args=['evening'],
            id='evening_quote',
            name='Evening Quote',
            replace_existing=True
        )

    def setup_schedule(self):
        """Setup the schedule based on configuration."""
        # Remove existing jobs
        try:
            self.scheduler.remove_job('morning_quote')
        except Exception:
            pass

        try:
            self.scheduler.remove_job('evening_quote')
        except Exception:
            pass

        # Setup new schedule based on config
        if config.schedule_window in ['morning', 'both']:
            self.schedule_morning_quote()

        if config.schedule_window in ['evening', 'both']:
            self.schedule_evening_quote()

        logger.info(f"Schedule setup complete: {config.schedule_window}")

    def get_next_run_time(self, job_id: str) -> datetime:
        """Get the next run time for a job.

        Args:
            job_id: Job ID ('morning_quote' or 'evening_quote')

        Returns:
            Next run datetime or None
        """
        try:
            job = self.scheduler.get_job(job_id)
            if job and job.next_run_time:
                return job.next_run_time
        except Exception:
            pass
        return None

    def list_jobs(self):
        """List all scheduled jobs."""
        jobs = self.scheduler.get_jobs()
        job_info = []

        for job in jobs:
            job_info.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None
            })

        return job_info

    def shutdown(self):
        """Shutdown the scheduler."""
        self.scheduler.shutdown()


# Global scheduler instance
_scheduler = None


def get_scheduler() -> QuoteScheduler:
    """Get the singleton scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = QuoteScheduler()
        _scheduler.setup_schedule()
    return _scheduler


if __name__ == "__main__":
    # Test the scheduler
    scheduler = get_scheduler()

    # List jobs
    jobs = scheduler.list_jobs()
    print("Scheduled Jobs:")
    for job in jobs:
        print(f"  - {job['name']}: {job['next_run_time']}")

    # Keep running
    try:
        import time
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nShutting down scheduler...")
        scheduler.shutdown()
