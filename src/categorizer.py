"""Event categorization and day analysis."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Tuple
from .calendar_service import CalendarEvent

WORK_KEYWORDS = ["reunião","meeting","sprint","review","planning","standup","projeto","trabalho","cliente","entrega","deploy","código","code","dev","eng"]
STUDY_KEYWORDS = ["aula","estudo","curso","lecture","prova","exam","classe","faculdade","universidade","escola","cálculo","tcc"]
HEALTH_KEYWORDS = ["academia","gym","médico","doctor","dentista","saúde","treino","corrida","yoga","pilates","fisio"]
TRAVEL_KEYWORDS = ["voo","flight","viagem","travel","hotel","aeroporto","airport","check-in","embarque"]
PERSONAL_KEYWORDS = ["almoço","jantar","café","aniversário","família","amigos","baska","casa","pessoal","birthday"]

def categorize_event(event: CalendarEvent) -> str:
    text = (event.title + " " + event.description).lower()
    if any(k in text for k in TRAVEL_KEYWORDS): return "Viagem"
    if any(k in text for k in HEALTH_KEYWORDS): return "Saúde"
    if any(k in text for k in STUDY_KEYWORDS): return "Estudos"
    if any(k in text for k in WORK_KEYWORDS): return "Trabalho"
    if any(k in text for k in PERSONAL_KEYWORDS): return "Pessoal"
    return "Outros"

@dataclass
class DayAnalysis:
    events: List[CalendarEvent]
    categories: List[str]
    total_hours: float
    free_blocks: List[Tuple[datetime, datetime]]
    workload: str
    conflicts: List[Tuple[CalendarEvent, CalendarEvent]]

def analyze_day(events: List[CalendarEvent]) -> DayAnalysis:
    timed = [e for e in events if not e.is_all_day]
    categories = [categorize_event(e) for e in events]

    total_minutes = sum((e.end - e.start).seconds // 60 for e in timed)
    total_hours = round(total_minutes / 60, 1)

    if total_hours < 3: workload = "Leve"
    elif total_hours < 6: workload = "Moderada"
    else: workload = "Pesada"

    conflicts = []
    for i, e1 in enumerate(timed):
        for e2 in timed[i+1:]:
            if e1.start < e2.end and e2.start < e1.end:
                conflicts.append((e1, e2))

    free_blocks = []
    if timed:
        sorted_events = sorted(timed, key=lambda e: e.start)
        work_start = sorted_events[0].start.replace(hour=7, minute=0, second=0, microsecond=0)
        work_end = sorted_events[0].start.replace(hour=22, minute=0, second=0, microsecond=0)
        cursor = work_start
        for ev in sorted_events:
            if ev.start > cursor + timedelta(minutes=30):
                free_blocks.append((cursor, ev.start))
            cursor = max(cursor, ev.end)
        if cursor < work_end - timedelta(minutes=30):
            free_blocks.append((cursor, work_end))

    return DayAnalysis(events=events, categories=categories, total_hours=total_hours,
                       free_blocks=free_blocks, workload=workload, conflicts=conflicts)
