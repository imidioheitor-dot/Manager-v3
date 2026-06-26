"""AI summary generation using Claude or OpenAI."""
import logging
from datetime import datetime
from typing import List
from .calendar_service import CalendarEvent
from .categorizer import DayAnalysis, categorize_event
from .config import config

logger = logging.getLogger(__name__)

def _format_time(dt: datetime) -> str:
    return dt.strftime("%H:%M")

def generate_daily_summary(analysis: DayAnalysis) -> str:
    events = [e for e in analysis.events if not e.is_all_day]
    all_day = [e for e in analysis.events if e.is_all_day]

    lines = ["*🗓 Meeting Guardian — Resumo do Dia*"]
    lines.append(f"*{datetime.now().strftime('%A, %d de %B de %Y')}*\n")

    name = "Heitor"
    lines.append(f"Bom dia, {name}! Hoje você possui *{len(events)} compromisso(s)*:\n")

    emoji_map = {"Trabalho": "💼", "Estudos": "📚", "Saúde": "🏋️", "Pessoal": "🌅", "Viagem": "✈️", "Outros": "📋"}
    for i, ev in enumerate(sorted(events, key=lambda e: e.start)):
        cat = categorize_event(ev)
        emoji = emoji_map.get(cat, "📋")
        lines.append(f"{emoji} {_format_time(ev.start)}–{_format_time(ev.end)} – {ev.title} _({cat})_")

    if all_day:
        lines.append("\n📌 *Eventos de dia inteiro:* " + ", ".join(e.title for e in all_day))

    lines.append("\n*Análise do dia:*")
    lines.append(f"• Carga: *{analysis.workload}* (~{analysis.total_hours}h em compromissos)")

    if analysis.free_blocks:
        best = max(analysis.free_blocks, key=lambda b: (b[1]-b[0]).seconds)
        lines.append(f"• Bloco livre principal: *{_format_time(best[0])} às {_format_time(best[1])}*")

    if analysis.conflicts:
        lines.append(f"• ⚠️ {len(analysis.conflicts)} conflito(s) detectado(s)!")
    else:
        lines.append("• Nenhum conflito detectado ✅")

    return "\n".join(lines)

def generate_reminder(event: CalendarEvent) -> str:
    cat = categorize_event(event)
    lines = [
        f"⏰ *Lembrete — 30 minutos*",
        f"\n*{event.title}*",
        f"🕐 {event.start.strftime('%H:%M')} – {event.end.strftime('%H:%M')}",
        f"📂 Categoria: {cat}",
    ]
    if event.location:
        lines.append(f"📍 Local: {event.location}")
    if event.attendees:
        lines.append(f"👥 Participantes: {', '.join(event.attendees[:5])}")
    if event.description:
        lines.append(f"📝 {event.description[:200]}")
    if event.meet_link:
        lines.append(f"🔗 Link: {event.meet_link}")
    return "\n".join(lines)
