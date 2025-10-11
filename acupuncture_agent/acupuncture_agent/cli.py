from __future__ import annotations

from datetime import datetime
from typing import Optional

import typer
from rich import print

from .agent import Agent
from .crud import create_practitioner, create_service, get_or_create_patient
from .db import Base, engine, session_scope
from .models import Practitioner, Service

app = typer.Typer(add_completion=False, help="Acupuncture Clinic Agent CLI")


@app.command()
def init_db() -> None:
    """Create database tables."""
    Base.metadata.create_all(bind=engine)
    print("[green]Database initialized[/green]")


@app.command("add-practitioner")
def add_practitioner(name: str, email: Optional[str] = None, phone: Optional[str] = None, specialties: Optional[str] = None) -> None:
    with session_scope() as s:
        p = create_practitioner(s, name=name, email=email, phone=phone, specialties=specialties)
        print(f"Added practitioner #{p.id}: {p.name}")


@app.command("add-service")
def add_service(name: str, duration_minutes: int = typer.Option(60), price_cents: int = typer.Option(0), description: Optional[str] = None) -> None:
    with session_scope() as s:
        svc = create_service(s, name=name, description=description, duration_minutes=duration_minutes, price_cents=price_cents)
        print(f"Added service #{svc.id}: {svc.name} ({svc.duration_minutes} min)")


@app.command()
def chat(message: str, name: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None) -> None:
    with session_scope() as s:
        agent = Agent()
        res = agent.handle_message(s, message=message, patient_name=name, patient_email=email, patient_phone=phone)
        print(f"[bold]Agent:[/bold] {res.reply}")
        if res.suggested_slots:
            for slot in res.suggested_slots:
                print(f" - {slot}")


@app.command()
def serve(host: str = "0.0.0.0", port: int = 8000, reload: bool = False) -> None:
    """Run the HTTP API server."""
    import uvicorn

    # Ensure tables exist; FastAPI startup also does this, but this is harmless
    Base.metadata.create_all(bind=engine)
    uvicorn.run("acupuncture_agent.api:app", host=host, port=port, reload=reload)


@app.command("seed-demo")
def seed_demo() -> None:
    """Seed demo practitioner and service for quick trials."""
    with session_scope() as s:
        p = create_practitioner(s, name="Dr. Lin", email="dr.lin@example.com", phone="+1-555-0101", specialties="acupuncture, cupping")
        svc = create_service(s, name="Acupuncture", description="Standard 60 min acupuncture session", duration_minutes=60, price_cents=9000)
        print(f"Seeded practitioner #{p.id} and service #{svc.id}.")


if __name__ == "__main__":
    app()
