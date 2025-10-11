from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException

from .agent import Agent
from .crud import (
    create_practitioner,
    create_service,
    create_appointment,
    list_business_hours,
)
from .db import Base, engine, get_session
from .models import Practitioner, Service
from .schemas import (
    AppointmentCreate,
    AppointmentRead,
    BusinessHoursRead,
    ChatRequest,
    ChatResponse,
    PractitionerCreate,
    PractitionerRead,
    ServiceCreate,
    ServiceRead,
)
from sqlalchemy.orm import Session

app = FastAPI(title="Acupuncture Clinic Agent")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, session: Session = Depends(get_session)) -> ChatResponse:
    agent = Agent()
    res = agent.handle_message(
        session,
        message=req.message,
        patient_name=req.patient_name,
        patient_email=req.patient_email,
        patient_phone=req.patient_phone,
    )
    return ChatResponse(reply=res.reply, suggested_slots=res.suggested_slots, intent=res.intent)


@app.post("/practitioners", response_model=PractitionerRead)
def add_practitioner(body: PractitionerCreate, session: Session = Depends(get_session)) -> PractitionerRead:
    p = create_practitioner(
        session,
        name=body.name,
        email=body.email,
        phone=body.phone,
        specialties=body.specialties,
    )
    return PractitionerRead.model_validate(p)


@app.post("/services", response_model=ServiceRead)
def add_service(body: ServiceCreate, session: Session = Depends(get_session)) -> ServiceRead:
    s = create_service(
        session,
        name=body.name,
        description=body.description,
        duration_minutes=body.duration_minutes,
        price_cents=body.price_cents,
    )
    return ServiceRead.model_validate(s)


@app.post("/appointments", response_model=AppointmentRead)
def add_appointment(body: AppointmentCreate, session: Session = Depends(get_session)) -> AppointmentRead:
    s: Service | None = session.get(Service, body.service_id)
    if not s:
        raise HTTPException(404, detail="Service not found")
    appt = create_appointment(
        session,
        patient_id=body.patient_id,
        practitioner_id=body.practitioner_id,
        service_id=body.service_id,
        start_time=body.start_time,
        duration_minutes=s.duration_minutes,
        notes=body.notes,
    )
    return AppointmentRead.model_validate(appt)


@app.get("/hours", response_model=List[BusinessHoursRead])
def get_hours(session: Session = Depends(get_session)) -> list[BusinessHoursRead]:
    return [BusinessHoursRead.model_validate(h) for h in list_business_hours(session)]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
