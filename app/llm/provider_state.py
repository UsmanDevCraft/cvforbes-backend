from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


@dataclass
class ProviderState:
    requests: int = 0
    minute_started: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    cooldown_until: datetime | None = None

    def reset_if_needed(self) -> None:
        now = datetime.now(tz=timezone.utc)

        if (now - self.minute_started).total_seconds() >= 60:
            self.requests = 0
            self.minute_started = now

    def increment(self) -> None:
        self.reset_if_needed()
        self.requests += 1

    def set_cooldown(self, seconds: int) -> None:
        self.cooldown_until = datetime.now(tz=timezone.utc) + timedelta(seconds=seconds)

    @property
    def is_in_cooldown(self) -> bool:
        if self.cooldown_until is None:
            return False

        return datetime.now(tz=timezone.utc) < self.cooldown_until
