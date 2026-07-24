from datetime import datetime, timedelta, timezone

from app.models.anonymous_user import AnonymousUser
from app.models.banned_ip import BannedIP
from app.models.generated_cv import GeneratedCV


class AnalyticsRepository:
    async def total_users(self) -> int:
        return await AnonymousUser.find_all().count()

    async def total_generations(self) -> int:
        return await GeneratedCV.find_all().count()

    async def active_today(self) -> int:
        today = datetime.now(timezone.utc).date()

        return await AnonymousUser.find(
            AnonymousUser.last_seen
            >= datetime.combine(
                today,
                datetime.min.time(),
                tzinfo=timezone.utc,
            )
        ).count()

    async def generations_today(self) -> int:
        today = datetime.now(timezone.utc).date()

        return await GeneratedCV.find(
            GeneratedCV.created_at
            >= datetime.combine(
                today,
                datetime.min.time(),
                tzinfo=timezone.utc,
            )
        ).count()

    async def temporary_bans(self) -> int:
        return await BannedIP.find(BannedIP.ban_type == "temporary").count()

    async def permanent_bans(self) -> int:
        return await BannedIP.find(BannedIP.ban_type == "permanent").count()

    async def recent_users(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[AnonymousUser], int]:
        query = AnonymousUser.find_all()
        total = await query.count()
        items = (
            await query.sort(-AnonymousUser.last_seen)
            .skip(offset)
            .limit(limit)
            .to_list()
        )
        return items, total

    async def recent_generations(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[GeneratedCV], int]:
        query = GeneratedCV.find_all()
        total = await query.count()
        items = (
            await query.sort(-GeneratedCV.created_at)
            .skip(offset)
            .limit(limit)
            .to_list()
        )
        return items, total

    async def active_bans(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[BannedIP], int]:
        query = BannedIP.find_all()
        total = await query.count()
        items = (
            await query.sort(-BannedIP.created_at).skip(offset).limit(limit).to_list()
        )
        return items, total

    async def daily_generations(
        self,
        days: int = 7,
    ):
        start = datetime.now(timezone.utc) - timedelta(days=days)

        generations = (
            await GeneratedCV.find(GeneratedCV.created_at >= start)
            .sort(GeneratedCV.created_at)
            .to_list()
        )

        return generations

    async def provider_usage(self):
        return await GeneratedCV.find_all().to_list()

    async def average_generation_time(self):
        return await GeneratedCV.find_all().to_list()
