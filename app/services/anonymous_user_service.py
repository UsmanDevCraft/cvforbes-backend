from datetime import datetime, timezone
from app.core.constants import MAX_DAILY_CVS
from app.core.exceptions import DailyLimitExceeded

from app.models.anonymous_user import AnonymousUser
from app.repositories.anonymous_user_repository import AnonymousRepository
from app.services.client_identity_service import ClientIdentity


class AnonymousUserService:
    def __init__(self):
        self.repository = AnonymousRepository()

    async def get_or_create(
        self,
        identity: ClientIdentity,
    ) -> AnonymousUser:

        user = await self.repository.get_by_fingerprint(identity.fingerprint)

        if user:
            user.last_seen = datetime.now(timezone.utc)

            await self.repository.save(user)

            return user

        user = await self.repository.create(
            fingerprint=identity.fingerprint,
            ip=identity.ip,
            user_agent=identity.user_agent,
            cookie_id=identity.cookie_id,
        )

        return user

    async def increment_usage(
        self,
        user: AnonymousUser,
    ) -> AnonymousUser:

        now = datetime.now(timezone.utc)

        user.requests_today += 1
        user.total_requests += 1
        user.last_request = now
        user.last_seen = now

        await self.repository.save(user)

        return user

    async def reset_daily_usage(
        self,
        user: AnonymousUser,
    ) -> AnonymousUser:

        today = datetime.now(timezone.utc).date()

        if user.last_reset.date() == today:
            return user

        user.requests_today = 0
        user.last_reset = datetime.now(timezone.utc)

        await self.repository.save(user)

        return user

    def check_daily_limit(
        self,
        user: AnonymousUser,
    ) -> bool:

        return user.requests_today >= MAX_DAILY_CVS

    async def update_email(
        self,
        user: AnonymousUser,
        email: str,
    ) -> AnonymousUser:

        if user.email == email:
            return user

        user.email = email

        await self.repository.save(user)

        return user

    async def validate_request(
        self,
        user: AnonymousUser,
    ) -> AnonymousUser:

        await self.reset_daily_usage(user)

        if self.check_daily_limit(user):
            raise DailyLimitExceeded()

        return user
