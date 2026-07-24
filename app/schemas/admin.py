from datetime import datetime

from pydantic import BaseModel


class StatsResponse(BaseModel):
    total_users: int
    active_today: int
    total_generations: int
    generated_today: int
    temporary_bans: int
    permanent_bans: int


class UserResponse(BaseModel):
    id: str
    ip: str
    email: str | None
    requests_today: int
    total_requests: int
    last_seen: datetime
    created_at: datetime


class PaginatedUserResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class GenerationResponse(BaseModel):
    id: str
    anonymous_user_id: str
    email: str | None
    filename: str
    provider: str
    model: str
    generation_time_ms: int
    ats_score: int
    parse_score: int
    status: str
    created_at: datetime


class PaginatedGenerationResponse(BaseModel):
    items: list[GenerationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BanResponse(BaseModel):
    id: str
    ip: str
    fingerprint: str
    reason: str
    ban_type: str
    expires_at: datetime | None
    created_at: datetime


class PaginatedBanResponse(BaseModel):
    items: list[BanResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AnalyticsResponse(BaseModel):
    daily_generations: dict[str, int]
    provider_usage: dict[str, int]
    average_generation_ms: int
