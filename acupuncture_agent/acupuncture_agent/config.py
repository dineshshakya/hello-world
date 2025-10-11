from __future__ import annotations

import os
from datetime import time


class Settings:
    """Basic runtime configuration.

    Uses environment variables when provided.
    """

    db_url: str
    timezone: str
    default_service_minutes: int

    # Default clinic hours (local time)
    default_open_time: time
    default_close_time: time

    def __init__(self) -> None:
        self.db_url = os.getenv("ACU_DB_URL", "sqlite:///./acupuncture_agent.db")
        self.timezone = os.getenv("ACU_TZ", "UTC")
        self.default_service_minutes = int(os.getenv("ACU_DEFAULT_SERVICE_MINUTES", "60"))
        self.default_open_time = time.fromisoformat(os.getenv("ACU_DEFAULT_OPEN", "09:00"))
        self.default_close_time = time.fromisoformat(os.getenv("ACU_DEFAULT_CLOSE", "17:00"))


settings = Settings()
