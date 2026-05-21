"""Pydantic schemas for hall availability search requests and responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SearchFilters(BaseModel):
    """Request filters for the hall search endpoint."""
    start_datetime: datetime = Field(..., description="Search start datetime")
    end_datetime: datetime = Field(..., description="Search end datetime")
    hall_id: UUID | None = Field(None, description="Optional hall ID filter")
    hall_name: str | None = Field(None, description="Optional hall name filter")
    facility_id: int | None = Field(None, description="Optional facility ID filter")
    facility_name: str | None = Field(None, description="Optional facility name filter")


class TimeSlot(BaseModel):
    """A free interval returned by the search engine."""
    start_time: datetime
    end_time: datetime
    duration_minutes: int


class SearchResultHall(BaseModel):
    """Availability summary for a single hall."""
    hall_id: UUID
    hall_name: str
    capacity: int
    floor: int
    available_slots: list[TimeSlot]


class SearchResult(BaseModel):
    """Full search response including the applied filters."""
    search_filters: SearchFilters
    results: list[SearchResultHall]
