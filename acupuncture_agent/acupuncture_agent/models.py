from __future__ import annotations

from datetime import datetime, time
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(40), nullable=True, unique=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="patient")


class Practitioner(Base):
    __tablename__ = "practitioners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    specialties: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="practitioner")


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="service")


class AppointmentStatusEnum(str):
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        CheckConstraint("end_time > start_time", name="ck_appt_time_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    practitioner_id: Mapped[int] = mapped_column(ForeignKey("practitioners.id", ondelete="CASCADE"), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), nullable=False)

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default=AppointmentStatusEnum.SCHEDULED, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    patient: Mapped[Patient] = relationship(back_populates="appointments")
    practitioner: Mapped[Practitioner] = relationship(back_populates="appointments")
    service: Mapped[Service] = relationship(back_populates="appointments")


class BusinessHours(Base):
    __tablename__ = "business_hours"
    __table_args__ = (
        UniqueConstraint("day_of_week", name="uq_hours_day"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Mon .. 6=Sun
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    open_time: Mapped[Optional[time]] = mapped_column(Time(timezone=False), nullable=True)
    close_time: Mapped[Optional[time]] = mapped_column(Time(timezone=False), nullable=True)


class Holiday(Base):
    __tablename__ = "holidays"
    __table_args__ = (
        UniqueConstraint("date", name="uq_holiday_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    closed_all_day: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
