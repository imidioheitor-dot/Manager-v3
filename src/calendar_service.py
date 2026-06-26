"""Google Calendar service for Meeting Guardian."""
import json
import os
import logging
from datetime import datetime, date
from typing import List, Optional
from dataclasses import dataclass, field
import pytz

from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from .config import config

logger = logging.getLogger(__name__)

SCOPES = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/gmail.send",
]

CALENDAR_SCOPES = [
        "https://www.googleapis.com/auth/calendar.readonly",
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
        # 1) Tenta OAuth token (GOOGLE_TOKEN_JSON)
        if config.google_token_json and config.google_token_json.strip():
                    try:
                                    token_data = json.loads(config.google_token_json)
                                    creds = Credentials(
                                        token=token_data.get("token"),
                                        refresh_token=token_data.get("refresh_token"),
                                        token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
                                        client_id=token_data.get("client_id"),
                                        client_secret=token_data.get("client_secret"),
                                        scopes=token_data.get("scopes", SCOPES),
                                    )
                                    if creds.expired and creds.refresh_token:
                                                        creds.refresh(Request())
                                                    if creds.valid:
                                                                        logger.info("Usando autenticacao OAuth (GOOGLE_TOKEN_JSON)")
                                                                        return creds
                    except Exception as e:
                                    logger.warning(f"Falha ao usar GOOGLE_TOKEN_JSON: {e}. Tentando Service Account...")

                # 2) Fallback: Service Account (GOOGLE_CREDENTIALS_JSON)
                if config.google_credentials_json and config.google_credentials_json.strip():
                            try:
                                            sa_info = json.loads(config.google_credentials_json)
                                            creds = service_account.Credentials.from_service_account_info(
                                                sa_info,
                                                scopes=CALENDAR_SCOPES,
                                            )
                                            logger.info("Usando autenticacao via Service Account (GOOGLE_CREDENTIALS_JSON)")
                                            return creds
except Exception as e:
            logger.error(f"Falha ao usar Service Account: {e}")

    # 3) Fallback: arquivos locais (desenvolvimento)
    token_path = "token.json"
    if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
                if creds and creds.expired and creds.refresh_token:
                                creds.refresh(Request())
                            if creds and creds.valid:
                                    return creds

    raise RuntimeError(
                "Nenhuma credencial Google valida encontrada. "
                "Configure GOOGLE_TOKEN_JSON (OAuth) ou GOOGLE_CREDENTIALS_JSON (Service Account) "
                "nas variaveis de ambiente do Railway. "
                "Para Service Account, lembre de compartilhar o calendario com o email da SA."
)


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
                        title=item.get("summary", "Sem titulo"),
                        start=start_dt,
                        end=end_dt,
                        description=item.get("description", ""),
                        location=item.get("location", ""),
                        attendees=attendees,
                        meet_link=meet_link,
                        is_all_day=is_all_day,
                        calendar_name=item.get("organizer", {}).get("displayName", ""),
        ))

    return events"""Google Calendar service for Meeting Guardian."""
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

SCOPES_SA = [
        "https://www.googleapis.com/auth/calendar.readonly",
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


def _get_credentials():
        """Return valid Google credentials.

            Priority:
                1. Service Account JSON (GOOGLE_CREDENTIALS_JSON) — recommended for server deploy
                    2. OAuth2 token JSON (GOOGLE_TOKEN_JSON) — user-auth flow
                        3. Local token.json file — local dev fallback
                            """

    # --- 1. Service Account ---
    if config.google_credentials_json:
                try:
                                creds_data = json.loads(config.google_credentials_json)
                                if creds_data.get("type") == "service_account":
                                                    from google.oauth2 import service_account
                                                    logger.info("Using Service Account credentials")
                                                    creds = service_account.Credentials.from_service_account_info(
                                                        creds_data, scopes=SCOPES_SA
                                                    )
                                                    return creds
    except (json.JSONDecodeError, KeyError) as exc:
            logger.warning("GOOGLE_CREDENTIALS_JSON parse error: %s", exc)

    # --- 2. OAuth2 token from env ---
    if config.google_token_json:
                try:
                                token_data = json.loads(config.google_token_json)
                                creds = Credentials(
                                    token=token_data.get("token"),
                                    refresh_token=token_data.get("refresh_token"),
                                    token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
                                    client_id=token_data.get("client_id"),
                                    client_secret=token_data.get("client_secret"),
                                    scopes=token_data.get("scopes", SCOPES),
                                )
                                if creds.expired and creds.refresh_token:
                                                    creds.refresh(Request())
                                                return creds
except (json.JSONDecodeError, KeyError) as exc:
            logger.warning("GOOGLE_TOKEN_JSON parse error: %s", exc)

    # --- 3. Local file fallback ---
    token_path = "token.json"
    if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds.expired and creds.refresh_token:
                        creds.refresh(Request())
        return creds

    raise RuntimeError(
                "No valid Google credentials found.\n"
                "Options:\n"
                "  1. Set GOOGLE_CREDENTIALS_JSON with a service account key JSON (recommended)\n"
                "  2. Set GOOGLE_TOKEN_JSON with a user OAuth2 token JSON\n"
                "  3. Place token.json in the working directory"
    )


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
                        start_dt = tz.localize(datetime.combine(
                                            date.fromisoformat(start_raw["date"]), datetime.min.time()
                        ))
            end_dt = tz.localize(datetime.combine(
                                date.fromisoformat(end_raw.get("date", start_raw["date"])), datetime.min.time()
            ))
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
                        title=item.get("summary", "Sem titulo"),
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
