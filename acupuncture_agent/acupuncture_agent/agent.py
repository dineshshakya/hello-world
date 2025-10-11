from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date
from difflib import get_close_matches
from typing import Optional

from sqlalchemy.orm import Session

from .config import settings
from .crud import (
    create_appointment,
    create_practitioner,
    create_service,
    get_or_create_patient,
    get_practitioner_by_name,
    get_service_by_name,
    list_practitioners,
    list_services,
)
from .models import Practitioner, Service
from .nlu import parse
from .scheduler import find_next_available_slots


@dataclass
class AgentResponse:
    reply: str
    suggested_slots: Optional[list[str]] = None
    intent: Optional[str] = None


def format_slot(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")


def choose_service(session: Session, hint: Optional[str]) -> Optional[Service]:
    services = list_services(session)
    if not services:
        return None
    if hint:
        names = [s.name for s in services]
        match = get_close_matches(hint, names, n=1, cutoff=0.5)
        if match:
            return next(s for s in services if s.name == match[0])
    # Fallback to default duration service
    return services[0]


def choose_practitioner(session: Session, hint: Optional[str]) -> Optional[Practitioner]:
    practitioners = list_practitioners(session)
    if not practitioners:
        return None
    if hint:
        names = [p.name for p in practitioners]
        match = get_close_matches(hint, names, n=1, cutoff=0.5)
        if match:
            return next(p for p in practitioners if p.name == match[0])
    return practitioners[0]


class Agent:
    def handle_message(
        self,
        session: Session,
        *,
        message: str,
        patient_name: Optional[str] = None,
        patient_email: Optional[str] = None,
        patient_phone: Optional[str] = None,
    ) -> AgentResponse:
        nlu = parse(message)
        intent = nlu.intent

        if intent in {"schedule_appointment", "availability_query"}:
            service = choose_service(session, nlu.service_name)
            practitioner = choose_practitioner(session, None)
            if not service or not practitioner:
                return AgentResponse(
                    reply="No services or practitioners are configured yet. Please add them first.",
                    intent=intent,
                )

            target_date = (nlu.date or datetime.now()).date()
            slots = find_next_available_slots(
                session,
                practitioners=[practitioner],
                service=service,
                start_date=target_date,
                days_ahead=7,
                per_day_slots=3,
            )
            if not slots:
                return AgentResponse(reply="No availability found in the next week.", intent=intent)

            formatted = [f"{p.name}: {format_slot(dt)}" for p, dt in slots]
            if intent == "availability_query":
                return AgentResponse(
                    reply=f"Here are upcoming {service.name} openings:",
                    suggested_slots=formatted,
                    intent=intent,
                )

            # schedule_appointment: if patient provided and a slot keyword like 'first'/'next'
            if patient_name:
                patient = get_or_create_patient(session, name=patient_name, email=patient_email, phone=patient_phone)
                # Choose first slot for simplicity
                chosen_prac, chosen_dt = slots[0]
                appt = create_appointment(
                    session,
                    patient_id=patient.id,
                    practitioner_id=chosen_prac.id,
                    service_id=service.id,
                    start_time=chosen_dt,
                    duration_minutes=service.duration_minutes,
                )
                return AgentResponse(
                    reply=f"Booked {service.name} with {chosen_prac.name} at {format_slot(appt.start_time)}.",
                    intent=intent,
                )
            else:
                return AgentResponse(
                    reply="Who should I book this for? Please provide your name (and optionally email/phone).",
                    suggested_slots=formatted,
                    intent=intent,
                )

        if intent == "hours_query":
            return AgentResponse(
                reply=(
                    f"We are typically open {settings.default_open_time.strftime('%H:%M')} - "
                    f"{settings.default_close_time.strftime('%H:%M')} Monday to Friday."
                ),
                intent=intent,
            )

        if intent == "pricing_query":
            services = list_services(session)
            if not services:
                return AgentResponse(reply="No services configured yet.", intent=intent)
            lines = [f"{s.name}: ${(s.price_cents/100):.2f} for {s.duration_minutes} min" for s in services]
            return AgentResponse(reply="Pricing:\n" + "\n".join(lines), intent=intent)

        if intent == "cancel_appointment":
            return AgentResponse(
                reply="To cancel, please provide the appointment ID or your scheduled date/time.",
                intent=intent,
            )

        return AgentResponse(
            reply="I can help you check availability, schedule, and answer hours or pricing questions.",
            intent=intent,
        )
