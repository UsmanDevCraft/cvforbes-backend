from datetime import datetime, timezone

from beanie import Document, Indexed
from pydantic import Field


class BannedIP(Document):
    ip: Indexed(str)

    fingerprint: str

    reason: str

    ban_type: str = "temporary"

    expires_at: datetime | None = None

    created_by: str = "system"

    notes: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "banned_ips"
