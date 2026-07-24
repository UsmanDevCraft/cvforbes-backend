from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number starting from 1"),
        page_size: int = Query(20, ge=1, le=50, description="Items per page (max 50)"),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size
