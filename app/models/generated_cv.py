from datetime import datetime, timezone

from beanie import Document
from pydantic import Field


class GeneratedCV(Document):
    anonymous_user_id: str

    email: str | None = None

    original_filename: str

    provider: str
    model: str

    generation_time_ms: int

    ats_score: int
    parse_score: int

    parsed_resume: dict

    tailored_resume: dict

    cover_letter: str

    status: str = "success"

    error: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "generated_cvs"
