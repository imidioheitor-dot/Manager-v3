"""Fan-out notifier for Meeting Guardian."""
import logging
from .slack_service import send_dm
from .email_service import send_email

logger = logging.getLogger(__name__)

def notify(subject: str, message: str) -> dict:
    results = {}
    results["slack"] = send_dm(message)
    results["email"] = send_email(subject, message)
    logger.info(f"Notification sent: {results}")
    return results
