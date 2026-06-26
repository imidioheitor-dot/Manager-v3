"""Slack service for Meeting Guardian."""
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .config import config

logger = logging.getLogger(__name__)

def send_dm(message: str) -> bool:
    if not config.slack_bot_token or not config.slack_user_id:
        logger.warning("Slack not configured, skipping.")
        return False
    try:
        client = WebClient(token=config.slack_bot_token)
        response = client.chat_postMessage(channel=config.slack_user_id, text=message, mrkdwn=True)
        logger.info(f"Slack message sent: {response['ts']}")
        return True
    except SlackApiError as e:
        logger.error(f"Slack error: {e.response['error']}")
        return False
