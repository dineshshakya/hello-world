from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from dateutil import parser as date_parser

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


@dataclass
class NLUResult:
    intent: str
    date: Optional[datetime] = None
    practitioner_name: Optional[str] = None
    service_name: Optional[str] = None
    cancel: bool = False
    reschedule: bool = False


INTENT_PATTERNS = {
    "schedule_appointment": [r"\b(book|schedule|appointment|reserve)\b"],
    "availability_query": [r"\bavailable|availability|openings|slots\b"],
    "hours_query": [r"\bhours|open|close|closing\b"],
    "pricing_query": [r"\bprice|cost|fee|pricing\b"],
    "cancel_appointment": [r"\bcancel\b"],
    "reschedule_appointment": [r"\breschedule\b"],
}

SERVICE_HINTS = {
    "acupuncture": ["acupuncture"],
    "cupping": ["cupping"],
    "herbal consultation": ["herbal", "herbs"],
    "initial intake": ["initial", "first time", "new patient"],
}


TIME_RE = re.compile(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", re.IGNORECASE)
DATE_RE = re.compile(r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b")


def normalize_intent(text: str) -> Optional[str]:
    for intent, patterns in INTENT_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                return intent
    return None


def extract_service(text: str) -> Optional[str]:
    t = text.lower()
    for service, hints in SERVICE_HINTS.items():
        for h in hints:
            if h in t:
                return service
    return None


def extract_date(text: str, now: Optional[datetime] = None) -> Optional[datetime]:
    now = now or datetime.now()
    t = text.lower()

    if "today" in t:
        return now
    if "tomorrow" in t:
        return now + timedelta(days=1)

    for i, wd in enumerate(WEEKDAYS):
        if f"next {wd}" in t or wd in t:
            days_ahead = (i - now.weekday() + 7) % 7
            if days_ahead == 0:
                days_ahead = 7  # move to next occurrence if same day mentioned
            return now + timedelta(days=days_ahead)

    # Try explicit date formats
    try:
        dt = date_parser.parse(text, fuzzy=True, default=now.replace(hour=9, minute=0, second=0, microsecond=0))
        return dt
    except Exception:
        pass

    return None


def extract_time(text: str, base: Optional[datetime]) -> Optional[datetime]:
    if base is None:
        base = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    m = TIME_RE.search(text)
    if not m:
        return base
    hour = int(m.group(1))
    minute = int(m.group(2) or 0)
    ampm = m.group(3)
    if ampm:
        ampm = ampm.lower()
        if ampm == "pm" and hour < 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0
    return base.replace(hour=hour, minute=minute, second=0, microsecond=0)


def parse(text: str, now: Optional[datetime] = None) -> NLUResult:
    intent = normalize_intent(text) or "unknown"
    service_name = extract_service(text)
    base_date = extract_date(text, now=now)
    date_time = extract_time(text, base=base_date) if base_date else None

    cancel = intent == "cancel_appointment"
    reschedule = intent == "reschedule_appointment"

    return NLUResult(
        intent=intent,
        date=date_time,
        service_name=service_name,
        cancel=cancel,
        reschedule=reschedule,
    )
