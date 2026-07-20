from datetime import datetime, timezone

from beanie import Document, Indexed
from pydantic import Field


class AnonymousUser(Document):
    fingerprint: Indexed(str, unique=True)

    ip: str
    user_agent: str
    cookie_id: str | None = None

    email: str | None = None

    requests_today: int = 0
    total_requests: int = 0

    abuse_score: int = 0
    is_banned: bool = False

    first_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_request: datetime | None = None

    last_reset: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "anonymous_users"
