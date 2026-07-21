from fastapi import APIRouter

from app.services.analytics_service import AnalyticsService

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

analytics_service = AnalyticsService()


@router.get("/stats")
async def dashboard_stats():
    return await analytics_service.dashboard_stats()


@router.get("/users")
async def users():
    return await analytics_service.recent_users()


@router.get("/generations")
async def generations(
    limit: int = 100,
):
    return await analytics_service.recent_generations(limit)


@router.get("/bans")
async def bans():
    return await analytics_service.active_bans()


@router.get("/analytics")
async def analytics():
    return await analytics_service.analytics()
