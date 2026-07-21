from fastapi import APIRouter, Depends, Request
from app.services.analytics_service import AnalyticsService
from app.schemas.pagination import PaginationParams
from app.core.responses import success_response
from app.schemas.api_response import ApiResponse
from app.schemas.admin import (
    StatsResponse,
    PaginatedUserResponse,
    PaginatedGenerationResponse,
    PaginatedBanResponse,
    AnalyticsResponse,
)
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
)

analytics_service = AnalyticsService()
limiter = Limiter(key_func=get_remote_address)


@router.get("/stats", response_model=ApiResponse[StatsResponse])
@limiter.limit("15/minute")
async def dashboard_stats(request: Request):
    stats = await analytics_service.dashboard_stats()
    return success_response(
        stats,
        "Dashboard statistics retrieved successfully.",
    )


@router.get("/users", response_model=ApiResponse[PaginatedUserResponse])
@limiter.limit("15/minute")
async def users(request: Request, pagination: PaginationParams = Depends()):
    users = await analytics_service.recent_users(
        page=pagination.page, page_size=pagination.page_size, offset=pagination.offset
    )
    return success_response(
        users,
        "Users retrieved successfully.",
    )


@router.get("/generations", response_model=ApiResponse[PaginatedGenerationResponse])
@limiter.limit("15/minute")
async def generations(request: Request, pagination: PaginationParams = Depends()):
    generations = await analytics_service.recent_generations(
        page=pagination.page, page_size=pagination.page_size, offset=pagination.offset
    )
    return success_response(
        generations,
        "Generations retrieved successfully.",
    )


@router.get("/bans", response_model=ApiResponse[PaginatedBanResponse])
@limiter.limit("15/minute")
async def bans(request: Request, pagination: PaginationParams = Depends()):
    bans = await analytics_service.active_bans(
        page=pagination.page, page_size=pagination.page_size, offset=pagination.offset
    )
    return success_response(
        bans,
        "Bans retrieved successfully.",
    )


@router.get("/analytics", response_model=ApiResponse[AnalyticsResponse])
@limiter.limit("20/minute")
async def analytics(request: Request):
    analytics = await analytics_service.analytics()
    return success_response(
        analytics,
        "Analytics retrieved successfully.",
    )
