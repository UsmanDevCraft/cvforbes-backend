from fastapi import APIRouter, Depends, Request
from app.services.analytics_service import AnalyticsService
from app.schemas.pagination import PaginationParams
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
)

analytics_service = AnalyticsService()
limiter = Limiter(key_func=get_remote_address)


@router.get("/stats")
@limiter.limit("15/minute")
async def dashboard_stats(request: Request):
    return await analytics_service.dashboard_stats()


@router.get("/users")
@limiter.limit("15/minute")
async def users(request: Request, pagination: PaginationParams = Depends()):
    return await analytics_service.recent_users(
        page=pagination.page, page_size=pagination.page_size, offset=pagination.offset
    )


@router.get("/generations")
@limiter.limit("15/minute")
async def generations(request: Request, pagination: PaginationParams = Depends()):
    return await analytics_service.recent_generations(
        page=pagination.page, page_size=pagination.page_size, offset=pagination.offset
    )


@router.get("/bans")
@limiter.limit("15/minute")
async def bans(request: Request, pagination: PaginationParams = Depends()):
    return await analytics_service.active_bans(
        page=pagination.page, page_size=pagination.page_size, offset=pagination.offset
    )


@router.get("/analytics")
@limiter.limit("20/minute")
async def analytics(request: Request):
    return await analytics_service.analytics()
