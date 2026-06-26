"""Configuration management for Meeting Guardian."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    # Google
    google_credentials_json: str = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
    google_token_json: str = os.getenv("GOOGLE_TOKEN_JSON", "")

    # Slack
    slack_bot_token: str = os.getenv("SLACK_BOT_TOKEN", "")
    slack_user_id: str = os.getenv("SLACK_USER_ID", "")

    # AI
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # Email
    notification_email: str = os.getenv("NOTIFICATION_EMAIL", "")
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")

    # Scheduler
    daily_summary_time: str = os.getenv("DAILY_SUMMARY_TIME", "06:00")
    timezone: str = os.getenv("TZ", "America/Sao_Paulo")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

config = Config()
