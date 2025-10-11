from __future__ import annotations

from datetime import datetime, date, time
from typing import Optional

from pydantic import BaseModel, Field


class ModelConfig:
    from_attributes = True


class PatientBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None

    model_config = ModelConfig


class PatientCreate(PatientBase):
    pass


class PatientRead(PatientBase):
    id: int


class PractitionerBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    specialties: Optional[str] = None
    is_active: bool = True

    model_config = ModelConfig


class PractitionerCreate(PractitionerBase):
    pass


class PractitionerRead(PractitionerBase):
    id: int


class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration_minutes: int
    price_cents: int = 0
    is_active: bool = True

    model_config = ModelConfig


class ServiceCreate(ServiceBase):
    pass


class ServiceRead(ServiceBase):
    id: int


class AppointmentBase(BaseModel):
    patient_id: int
    practitioner_id: int
    service_id: int
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None

    model_config = ModelConfig


class AppointmentCreate(BaseModel):
    patient_id: int
    practitioner_id: int
    service_id: int
    start_time: datetime
    notes: Optional[str] = None


class AppointmentRead(AppointmentBase):
    id: int
    status: str


class BusinessHoursBase(BaseModel):
    day_of_week: int  # 0..6
    is_closed: bool = False
    open_time: Optional[time] = None
    close_time: Optional[time] = None

    model_config = ModelConfig


class BusinessHoursRead(BusinessHoursBase):
    id: int


class HolidayBase(BaseModel):
    date: date
    name: Optional[str] = None
    closed_all_day: bool = True

    model_config = ModelConfig


class HolidayRead(HolidayBase):
    id: int


class ChatRequest(BaseModel):
    message: str = Field(..., description="User input message")
    patient_name: Optional[str] = None
    patient_email: Optional[str] = None
    patient_phone: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    suggested_slots: Optional[list[str]] = None
    intent: Optional[str] = None
