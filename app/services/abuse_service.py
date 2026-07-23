from datetime import datetime, timezone, timedelta

from app.repositories.banned_ip_repository import BannedRepository
from app.services.client_identity_service import ClientIdentity
from app.models.anonymous_user import AnonymousUser
from app.repositories.anonymous_user_repository import AnonymousRepository

TEMP_BAN_SCORE = 70
PERMANENT_BAN_SCORE = 100


class AbuseService:
    def __init__(self):

        self.repository = BannedRepository()
        self.user_repository = AnonymousRepository()

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

    async def increase_score(
        self,
        user: AnonymousUser,
        identity: ClientIdentity,
        points: int,
        reason: str,
    ) -> AnonymousUser:
        """
        Increase a user's abuse score and automatically
        evaluate whether they should be banned.
        """

        user.abuse_score += points

        await self.user_repository.save(user)

        await self.evaluate(
            user=user,
            identity=identity,
            reason=reason,
        )

        return user

    async def evaluate(
        self,
        user: AnonymousUser,
        identity: ClientIdentity,
        reason: str,
    ) -> None:
        """
        Evaluate the user's abuse score and apply
        temporary or permanent bans when thresholds are reached.
        """

        # Permanent ban
        if user.abuse_score >= self.PERMANENT_BAN_SCORE:
            if not await self.is_banned(identity.fingerprint):
                await self.permanent_ban(
                    identity=identity,
                    reason=reason,
                )

            user.is_banned = True
            await self.user_repository.save(user)
            return

        # Temporary ban
        if user.abuse_score >= self.TEMP_BAN_SCORE:
            if not await self.is_banned(identity.fingerprint):
                await self.temporary_ban(
                    identity=identity,
                    reason=reason,
                )

            user.is_banned = True
            await self.user_repository.save(user)
            return
