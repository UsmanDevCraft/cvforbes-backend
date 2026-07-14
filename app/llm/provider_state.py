from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class ProviderState:
    requests: int = 0
    minute_started: datetime = field(default_factory=datetime.utcnow)
    cooldown_until: datetime | None = None

    def reset_if_needed(self):
        now = datetime.utcnow()

        if (now - self.minute_started).total_seconds() >= 60:
            self.requests = 0
            self.minute_started = now

    def increment(self):
        self.reset_if_needed()
        self.requests += 1

    def set_cooldown(self, seconds: int):
        self.cooldown_until = datetime.utcnow() + timedelta(seconds=seconds)

    @property
    def is_in_cooldown(self):
        if self.cooldown_until is None:
            return False

        return datetime.utcnow() < self.cooldown_until
