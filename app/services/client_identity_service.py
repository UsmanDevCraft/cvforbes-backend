from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass

from fastapi import Request

COOKIE_NAME = "cvforbes_id"


@dataclass(slots=True)
class ClientIdentity:
    ip: str
    user_agent: str
    cookie_id: str
    fingerprint: str


class ClientIdentityService:
    """
    Responsible ONLY for identifying anonymous clients.

    This service should NEVER:
    - Talk to MongoDB
    - Rate limit users
    - Ban users
    """

    def get_client_ip(self, request: Request) -> str:
        """
        For local development we trust request.client.host.

        When deploying behind Cloudflare/Nginx,
        this method is the ONLY place that changes.
        """

        return request.client.host if request.client else "unknown"

    def get_user_agent(self, request: Request) -> str:
        return request.headers.get("User-Agent", "unknown")

    def get_cookie(self, request: Request) -> str | None:
        return request.cookies.get(COOKIE_NAME)

    def generate_cookie(self) -> str:
        return uuid.uuid4().hex

    def generate_fingerprint(
        self,
        ip: str,
        user_agent: str,
        cookie_id: str,
    ) -> str:
        raw = f"{ip}:{user_agent}:{cookie_id}"

        return hashlib.sha256(raw.encode()).hexdigest()

    def get_identity(self, request: Request) -> ClientIdentity:
        ip = self.get_client_ip(request)

        user_agent = self.get_user_agent(request)

        cookie = self.get_cookie(request)

        if cookie is None:
            cookie = self.generate_cookie()

        fingerprint = self.generate_fingerprint(
            ip=ip,
            user_agent=user_agent,
            cookie_id=cookie,
        )

        return ClientIdentity(
            ip=ip,
            user_agent=user_agent,
            cookie_id=cookie,
            fingerprint=fingerprint,
        )
