"""Meeting Guardian entry point."""
import logging
import sys
from .config import config

logging.basicConfig(
    level=getattr(logging, config.log_level, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

def main():
    args = sys.argv[1:]
    command = args[0] if args else "run"

    if command == "run":
        logger.info("Starting Meeting Guardian...")
        from .scheduler import start_scheduler
        start_scheduler()

    elif command == "summary":
        logger.info("Generating one-off daily digest...")
        from .guardian import run_daily_digest
        run_daily_digest()

    elif command == "test-auth":
        logger.info("Testing Google auth...")
        from .calendar_service import get_events_for_day
        events = get_events_for_day()
        print(f"Auth OK — {len(events)} events today.")

    else:
        print(f"Unknown command: {command}")
        print("Usage: python -m src.main [run|summary|test-auth]")
        sys.exit(1)

if __name__ == "__main__":
    main()
