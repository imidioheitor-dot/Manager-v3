"""Email service for Meeting Guardian."""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import config

logger = logging.getLogger(__name__)

def send_email(subject: str, body: str) -> bool:
    if not config.notification_email or not config.smtp_password:
        logger.warning("Email not configured, skipping.")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = config.smtp_username
        msg["To"] = config.notification_email
        msg.attach(MIMEText(body, "plain"))
        html = f"<html><body><pre style='font-family:sans-serif'>{body}</pre></body></html>"
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
            server.starttls()
            server.login(config.smtp_username, config.smtp_password)
            server.sendmail(config.smtp_username, config.notification_email, msg.as_string())
        logger.info(f"Email sent to {config.notification_email}")
        return True
    except Exception as e:
        logger.error(f"Email error: {e}")
        return False
