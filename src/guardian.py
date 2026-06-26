"""Main guardian orchestration logic."""
import logging
from datetime import datetime, timedelta
from typing import Set
import pytz

from .calendar_service import get_events_for_day, CalendarEvent
from .categorizer import analyze_day
from .ai_summary_service import generate_daily_summary, generate_reminder
from .notifier import notify
from .config import config

logger = logging.getLogger(__name__)

_reminded_events: Set[str] = set()

def run_daily_digest() -> None:
    logger.info("Running daily digest...")
    tz = pytz.timezone(config.timezone)
    events = get_events_for_day()
    analysis = analyze_day(events)
    summary = generate_daily_summary(analysis)
    date_str = datetime.now(tz).strftime("%d/%m/%Y")
    notify(f"Meeting Guardian — {date_str}", summary)
    logger.info(f"Daily digest sent: {len(events)} events")

def run_reminder_sweep() -> None:
    tz = pytz.timezone(config.timezone)
    now = datetime.now(tz)
    events = get_events_for_day()

    for event in events:
        if event.is_all_day:
            continue
        minutes_until = (event.start - now).total_seconds() / 60
        if 25 <= minutes_until <= 35 and event.id not in _reminded_events:
            reminder = generate_reminder(event)
            notify(f"⏰ Em 30min: {event.title}", reminder)
            _reminded_events.add(event.id)
            logger.info(f"Reminder sent for: {event.title}")
