import math
from collections import Counter

from app.repositories.analytics_repository import AnalyticsRepository


class AnalyticsService:
    def __init__(self):
        self.repository = AnalyticsRepository()

    def _build_paginated_response(self, items, total: int, page: int, page_size: int):
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if page_size > 0 else 0,
        }

    async def dashboard_stats(self):
        return {
            "total_users": await self.repository.total_users(),
            "active_today": await self.repository.active_today(),
            "total_generations": await self.repository.total_generations(),
            "generated_today": await self.repository.generations_today(),
            "temporary_bans": await self.repository.temporary_bans(),
            "permanent_bans": await self.repository.permanent_bans(),
        }

    async def recent_users(self, page: int = 1, page_size: int = 20, offset: int = 0):
        users, total = await self.repository.recent_users(
            limit=page_size, offset=offset
        )

        formatted_items = [
            {
                "id": str(user.id),
                "ip": user.ip,
                "email": user.email,
                "requests_today": user.requests_today,
                "total_requests": user.total_requests,
                "last_seen": user.last_seen,
                "created_at": user.created_at,
            }
            for user in users
        ]

        return self._build_paginated_response(formatted_items, total, page, page_size)

    async def recent_generations(
        self, page: int = 1, page_size: int = 20, offset: int = 0
    ):
        generations, total = await self.repository.recent_generations(
            limit=page_size, offset=offset
        )

        formatted_items = [
            {
                "id": str(g.id),
                "anonymous_user_id": g.anonymous_user_id,
                "email": g.email,
                "filename": g.original_filename,
                "provider": g.provider,
                "model": g.model,
                "generation_time_ms": g.generation_time_ms,
                "ats_score": g.ats_score,
                "parse_score": g.parse_score,
                "status": g.status,
                "created_at": g.created_at,
            }
            for g in generations
        ]

        return self._build_paginated_response(formatted_items, total, page, page_size)

    async def active_bans(self, page: int = 1, page_size: int = 20, offset: int = 0):
        bans, total = await self.repository.active_bans(limit=page_size, offset=offset)

        formatted_items = [
            {
                "id": str(ban.id),
                "ip": ban.ip,
                "fingerprint": ban.fingerprint,
                "reason": ban.reason,
                "ban_type": ban.ban_type,
                "expires_at": ban.expires_at,
                "created_at": ban.created_at,
            }
            for ban in bans
        ]

        return self._build_paginated_response(formatted_items, total, page, page_size)

    async def analytics(self):
        generations = await self.repository.daily_generations()
        providers = await self.repository.provider_usage()
        avg = await self.repository.average_generation_time()

        provider_counter = Counter(g.provider for g in providers)
        avg_ms = sum(g.generation_time_ms for g in avg) / len(avg) if avg else 0

        daily = {}
        for g in generations:
            key = g.created_at.strftime("%Y-%m-%d")
            daily[key] = daily.get(key, 0) + 1

        return {
            "daily_generations": daily,
            "provider_usage": provider_counter,
            "average_generation_ms": round(avg_ms),
        }
