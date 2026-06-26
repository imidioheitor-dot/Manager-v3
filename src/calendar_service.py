"""Google Calendar service for Meeting Guardian."""
import json
import os
import logging
from datetime import datetime, date
from typing import List, Optional
from dataclasses import dataclass, field
import pytz

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from .config import config

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

@dataclass
class CalendarEvent:
    id: str
    title: str
    start: datetime
    end: datetime
    description: str = ""
    location: str = ""
    attendees: List[str] = field(default_factory=list)
    meet_link: str = ""
    is_all_day: bool = False
    calendar_name: str = ""

def _get_credentials() -> Credentials:
    creds = None
    token_path = "token.json"
    creds_path = "credentials.json"

    # Try env vars first
    if config.google_token_json:
        token_data = json.loads(config.google_token_json)
        creds = Credentials(
            token=token_data.get("token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=token_data.get("client_id"),
            client_secret=token_data.get("client_secret"),
            scopes=token_data.get("scopes", SCOPES),
        )
    elif os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds or not creds.valid:
        raise RuntimeError("No valid Google credentials. Run: python -m src.main test-auth")

    return creds

def get_events_for_day(target_date: Optional[date] = None) -> List[CalendarEvent]:
    tz = pytz.timezone(config.timezone)
    if target_date is None:
        target_date = datetime.now(tz).date()

    start_of_day = tz.localize(datetime.combine(target_date, datetime.min.time()))
    end_of_day = tz.localize(datetime.combine(target_date, datetime.max.time()))

    creds = _get_credentials()
    service = build("calendar", "v3", credentials=creds)

    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_of_day.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = []
    for item in events_result.get("items", []):
        start_raw = item.get("start", {})
        end_raw = item.get("end", {})

        is_all_day = "date" in start_raw and "dateTime" not in start_raw

        if is_all_day:
            start_dt = tz.localize(datetime.combine(date.fromisoformat(start_raw["date"]), datetime.min.time()))
            end_dt = tz.localize(datetime.combine(date.fromisoformat(end_raw.get("date", start_raw["date"])), datetime.min.time()))
        else:
            start_dt = datetime.fromisoformat(start_raw["dateTime"]).astimezone(tz)
            end_dt = datetime.fromisoformat(end_raw["dateTime"]).astimezone(tz)

        meet_link = ""
        for ep in item.get("conferenceData", {}).get("entryPoints", []):
            if ep.get("entryPointType") == "video":
                meet_link = ep.get("uri", "")
                break

        attendees = [
            a.get("displayName", a.get("email", ""))
            for a in item.get("attendees", [])
            if not a.get("self", False)
        ]

        events.append(CalendarEvent(
            id=item["id"],
            title=item.get("summary", "Sem título"),
            start=start_dt,
            end=end_dt,
            description=item.get("description", ""),
            location=item.get("location", ""),
            attendees=attendees,
            meet_link=meet_link,
            is_all_day=is_all_day,
            calendar_name=item.get("organizer", {}).get("displayName", ""),
        ))

    return events
