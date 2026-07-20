from datetime import datetime, timezone, timedelta

from app.repositories.banned_ip_repository import BannedRepository
from app.services.client_identity_service import ClientIdentity


class AbuseService:
    def __init__(self):

        self.repository = BannedRepository()

    async def get_active_ban(
        self,
        fingerprint: str,
    ):

        ban = await self.repository.get_by_fingerprint(fingerprint)

        if not ban:
            return None

        if ban.expires_at and ban.expires_at < datetime.now(timezone.utc):
            await self.repository.delete(ban)
            return None

        return ban

    async def temporary_ban(
        self,
        identity: ClientIdentity,
        reason: str,
        hours: int = 24,
    ):
        await self.repository.create(
            ip=identity.ip,
            fingerprint=identity.fingerprint,
            reason=reason,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=hours),
        )

    async def permanent_ban(
        self,
        identity: ClientIdentity,
        reason: str,
    ):
        await self.repository.create(
            ip=identity.ip,
            fingerprint=identity.fingerprint,
            reason=reason,
            ban_type="permanent",
        )

    async def is_banned(
        self,
        fingerprint: str,
    ) -> bool:
        ban = await self.get_active_ban(fingerprint)

        return ban is not None
