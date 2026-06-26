"""APScheduler configuration for Meeting Guardian."""
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from .guardian import run_daily_digest, run_reminder_sweep
from .config import config

logger = logging.getLogger(__name__)

def start_scheduler() -> None:
    tz = pytz.timezone(config.timezone)
    scheduler = BlockingScheduler(timezone=tz)

    hour, minute = config.daily_summary_time.split(":")
    scheduler.add_job(
        run_daily_digest,
        CronTrigger(hour=int(hour), minute=int(minute), timezone=tz),
        id="daily_digest",
        name="Daily Digest",
        replace_existing=True,
    )

    scheduler.add_job(
        run_reminder_sweep,
        CronTrigger(minute="*/15", hour="6-23", timezone=tz),
        id="reminder_sweep",
        name="Reminder Sweep",
        replace_existing=True,
    )

    logger.info(f"Scheduler started. Daily digest at {config.daily_summary_time} {config.timezone}")
    scheduler.start()
