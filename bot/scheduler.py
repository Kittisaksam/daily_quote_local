"""Scheduler module for sending daily quotes at scheduled times."""
import logging
import random
from datetime import datetime, time
from pathlib import Path
from typing import Optional

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

# Scheduler configuration
SCHEDULER_TIMEZONE = 'Asia/Bangkok'

# Job IDs and names
JOBS = {
    'morning': {'id': 'morning_quote', 'name': 'Morning Quote'},
    'evening': {'id': 'evening_quote', 'name': 'Evening Quote'}
}


class QuoteScheduler:
    """Scheduler for sending daily quotes."""

    def __init__(self, stats_dir: Optional[Path] = None):
        """Initialize the scheduler.

        Args:
            stats_dir: Directory for scheduler database (defaults to data directory)
        """
        db_dir = stats_dir or config.stats_file.parent
        job_stores = {
            'default': SQLAlchemyJobStore(url=f'sqlite:///{db_dir}/scheduler.sqlite')
        }

        self.scheduler = BackgroundScheduler(
            jobstores=job_stores,
            timezone=SCHEDULER_TIMEZONE
        )
        self.scheduler.start()

    @staticmethod
    def _parse_time(time_str: str) -> time:
        """Parse time string (HH:MM) to time object.

        Args:
            time_str: Time string in HH:MM format

        Returns:
            datetime.time object
        """
        hour, minute = map(int, time_str.split(':'))
        return time(hour=hour, minute=minute)

    @staticmethod
    def _get_random_time_in_window(start_str: str, end_str: str) -> time:
        """Get a random time within a time window.

        Args:
            start_str: Start time in HH:MM format
            end_str: End time in HH:MM format

        Returns:
            datetime.time object with random time
        """
        start_time = QuoteScheduler._parse_time(start_str)
        end_time = QuoteScheduler._parse_time(end_str)

        # Convert to minutes since midnight
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute

        # Get random minute in range and convert back to time
        random_minutes = random.randint(start_minutes, end_minutes)
        return time(hour=random_minutes // 60, minute=random_minutes % 60)

    def _remove_job(self, job_id: str):
        """Remove a job if it exists.

        Args:
            job_id: Job identifier to remove
        """
        try:
            self.scheduler.remove_job(job_id)
        except Exception:
            pass

    def send_daily_quote(self, time_period: str = "unknown"):
        """Send a daily quote.

        Args:
            time_period: 'morning' or 'evening'
        """
        logger.info(f"Sending scheduled {time_period} quote...")

        quote = get_quote(language=config.quote_language)
        success = send_quote_sync(quote, time_period=time_period)

        if success:
            logger.info(f"Successfully sent {time_period} quote")
        else:
            logger.error(f"Failed to send {time_period} quote")

    def _schedule_quote(self, period: str, start_time: str, end_time: str):
        """Schedule a daily quote within a time window.

        Args:
            period: 'morning' or 'evening'
            start_time: Start time in HH:MM format
            end_time: End time in HH:MM format
        """
        random_time = self._get_random_time_in_window(start_time, end_time)
        job_info = JOBS[period]

        logger.info(f"Scheduling {period} quote at {random_time}")

        self.scheduler.add_job(
            self.send_daily_quote,
            trigger=CronTrigger(hour=random_time.hour, minute=random_time.minute),
            args=[period],
            id=job_info['id'],
            name=job_info['name'],
            replace_existing=True
        )

    def setup_schedule(self):
        """Setup the schedule based on configuration."""
        # Remove existing jobs
        for job_info in JOBS.values():
            self._remove_job(job_info['id'])

        # Setup new schedule based on config
        if config.schedule_window in ('morning', 'both'):
            self._schedule_quote('morning', config.morning_start, config.morning_end)

        if config.schedule_window in ('evening', 'both'):
            self._schedule_quote('evening', config.evening_start, config.evening_end)

        logger.info(f"Schedule setup complete: {config.schedule_window}")

    def get_next_run_time(self, job_id: str) -> Optional[datetime]:
        """Get the next run time for a job.

        Args:
            job_id: Job ID ('morning_quote' or 'evening_quote')

        Returns:
            Next run datetime or None
        """
        try:
            job = self.scheduler.get_job(job_id)
            return job.next_run_time if job else None
        except Exception:
            return None

    def list_jobs(self):
        """List all scheduled jobs.

        Returns:
            List of dictionaries with job information
        """
        jobs = self.scheduler.get_jobs()
        return [
            {
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None
            }
            for job in jobs
        ]

    def shutdown(self):
        """Shutdown the scheduler."""
        self.scheduler.shutdown()


# Global scheduler instance
_scheduler: Optional[QuoteScheduler] = None


def get_scheduler() -> QuoteScheduler:
    """Get the singleton scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = QuoteScheduler()
        _scheduler.setup_schedule()
    return _scheduler


if __name__ == "__main__":
    import time as time_module

    # Test the scheduler
    scheduler = get_scheduler()

    # List jobs
    jobs = scheduler.list_jobs()
    print("Scheduled Jobs:")
    for job in jobs:
        print(f"  - {job['name']}: {job['next_run_time']}")

    # Keep running
    try:
        while True:
            time_module.sleep(60)
    except KeyboardInterrupt:
        print("\nShutting down scheduler...")
        scheduler.shutdown()
