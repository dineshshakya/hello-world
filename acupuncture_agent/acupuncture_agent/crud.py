from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional, Sequence

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from .models import Appointment, Patient, Practitioner, Service, BusinessHours


# Patients

def get_or_create_patient(session: Session, *, name: str, email: Optional[str], phone: Optional[str]) -> Patient:
    if email:
        patient = session.execute(select(Patient).where(Patient.email == email)).scalar_one_or_none()
        if patient:
            return patient
    if phone:
        patient = session.execute(select(Patient).where(Patient.phone == phone)).scalar_one_or_none()
        if patient:
            return patient
    patient = Patient(name=name, email=email, phone=phone)
    session.add(patient)
    session.flush()
    return patient


def get_patient_by_id(session: Session, patient_id: int) -> Optional[Patient]:
    return session.get(Patient, patient_id)


# Practitioners

def list_practitioners(session: Session) -> Sequence[Practitioner]:
    return session.execute(select(Practitioner).where(Practitioner.is_active == True)).scalars().all()


def get_practitioner_by_name(session: Session, name: str) -> Optional[Practitioner]:
    return session.execute(select(Practitioner).where(Practitioner.name.ilike(name))).scalar_one_or_none()


def create_practitioner(session: Session, *, name: str, email: Optional[str], phone: Optional[str], specialties: Optional[str]) -> Practitioner:
    practitioner = Practitioner(name=name, email=email, phone=phone, specialties=specialties, is_active=True)
    session.add(practitioner)
    session.flush()
    return practitioner


# Services

def list_services(session: Session) -> Sequence[Service]:
    return session.execute(select(Service).where(Service.is_active == True)).scalars().all()


def get_service_by_name(session: Session, name: str) -> Optional[Service]:
    return session.execute(select(Service).where(Service.name.ilike(name))).scalar_one_or_none()


def create_service(session: Session, *, name: str, description: Optional[str], duration_minutes: int, price_cents: int) -> Service:
    service = Service(name=name, description=description, duration_minutes=duration_minutes, price_cents=price_cents, is_active=True)
    session.add(service)
    session.flush()
    return service


# Appointments

def list_appointments_on_day(session: Session, practitioner_id: int, day_start: datetime, day_end: datetime) -> Sequence[Appointment]:
    return (
        session.execute(
            select(Appointment)
            .where(
                Appointment.practitioner_id == practitioner_id,
                Appointment.status == "scheduled",
                or_(
                    and_(Appointment.start_time >= day_start, Appointment.start_time < day_end),
                    and_(Appointment.end_time > day_start, Appointment.end_time <= day_end),
                    and_(Appointment.start_time <= day_start, Appointment.end_time >= day_end),
                ),
            )
            .order_by(Appointment.start_time.asc())
        )
        .scalars()
        .all()
    )


def has_conflict(session: Session, practitioner_id: int, start_time: datetime, end_time: datetime) -> bool:
    appts = (
        session.execute(
            select(Appointment).where(
                Appointment.practitioner_id == practitioner_id,
                Appointment.status == "scheduled",
                or_(
                    and_(Appointment.start_time < end_time, Appointment.end_time > start_time),
                ),
            )
        )
        .scalars()
        .first()
    )
    return appts is not None


def create_appointment(
    session: Session,
    *,
    patient_id: int,
    practitioner_id: int,
    service_id: int,
    start_time: datetime,
    duration_minutes: int,
    notes: Optional[str] = None,
) -> Appointment:
    end_time = start_time + timedelta(minutes=duration_minutes)
    if has_conflict(session, practitioner_id, start_time, end_time):
        raise ValueError("Time slot conflicts with existing appointment")
    appt = Appointment(
        patient_id=patient_id,
        practitioner_id=practitioner_id,
        service_id=service_id,
        start_time=start_time,
        end_time=end_time,
        status="scheduled",
        notes=notes,
    )
    session.add(appt)
    session.flush()
    return appt


def cancel_appointment(session: Session, appointment_id: int) -> Optional[Appointment]:
    appt = session.get(Appointment, appointment_id)
    if not appt:
        return None
    appt.status = "cancelled"
    session.flush()
    return appt


# Business hours

def upsert_business_hours(session: Session, *, day_of_week: int, is_closed: bool, open_time: Optional[str], close_time: Optional[str]) -> None:
    hours = session.execute(select(BusinessHours).where(BusinessHours.day_of_week == day_of_week)).scalar_one_or_none()
    if hours is None:
        hours = BusinessHours(day_of_week=day_of_week)
        session.add(hours)
    hours.is_closed = is_closed
    hours.open_time = open_time
    hours.close_time = close_time
    session.flush()


def list_business_hours(session: Session) -> Sequence[BusinessHours]:
    return session.execute(select(BusinessHours).order_by(BusinessHours.day_of_week.asc())).scalars().all()
