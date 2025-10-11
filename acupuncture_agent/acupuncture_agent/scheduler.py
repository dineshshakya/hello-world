from __future__ import annotations

from datetime import datetime, time, timedelta, date
from typing import Optional, Sequence

from sqlalchemy.orm import Session

from .config import settings
from .crud import list_appointments_on_day
from .models import BusinessHours, Practitioner, Service

WEEKDAY_NAME_TO_IDX = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def get_business_hours_for_date(session: Session, d: date) -> tuple[bool, Optional[time], Optional[time]]:
    weekday = d.weekday()
    hours = session.query(BusinessHours).filter(BusinessHours.day_of_week == weekday).one_or_none()
    if hours is None:
        return False, settings.default_open_time, settings.default_close_time
    if hours.is_closed:
        return True, None, None
    return False, hours.open_time, hours.close_time


def generate_slots(
    session: Session,
    *,
    practitioner_id: int,
    service_minutes: int,
    day: date,
    slot_granularity_minutes: int = 15,
    max_slots: int = 8,
) -> list[datetime]:
    is_closed, open_t, close_t = get_business_hours_for_date(session, day)
    if is_closed or open_t is None or close_t is None:
        return []

    day_start = datetime.combine(day, open_t)
    day_end = datetime.combine(day, close_t)

    taken = list_appointments_on_day(session, practitioner_id, day_start, day_end)
    blocked: list[tuple[datetime, datetime]] = [(a.start_time, a.end_time) for a in taken]

    slots: list[datetime] = []
    cursor = day_start
    step = timedelta(minutes=slot_granularity_minutes)
    service_delta = timedelta(minutes=service_minutes)

    while cursor + service_delta <= day_end and len(slots) < max_slots:
        conflict = False
        for s, e in blocked:
            if cursor < e and (cursor + service_delta) > s:
                conflict = True
                break
        if not conflict:
            slots.append(cursor)
        cursor += step

    return slots


def find_next_available_slots(
    session: Session,
    *,
    practitioners: Sequence[Practitioner],
    service: Service,
    start_date: date,
    days_ahead: int = 14,
    per_day_slots: int = 3,
) -> list[tuple[Practitioner, datetime]]:
    results: list[tuple[Practitioner, datetime]] = []
    for day_offset in range(days_ahead + 1):
        d = start_date + timedelta(days=day_offset)
        for p in practitioners:
            day_slots = generate_slots(session, practitioner_id=p.id, service_minutes=service.duration_minutes, day=d, max_slots=per_day_slots)
            for slot in day_slots:
                results.append((p, slot))
    return results
