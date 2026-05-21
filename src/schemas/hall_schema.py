"""Pydantic schemas for hall and hall-facility APIs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field
from pydantic import ConfigDict


class HallCreate(BaseModel):
    """Payload for creating a hall."""
    name: str
    capacity: int
    floor: int
    is_active: bool = True


class HallUpdate(BaseModel):
    """Payload for updating a hall."""
    hall_name: str
    name: str | None = None
    capacity: int | None = None
    floor: int | None = None
    is_active: bool | None = None


class FacilitySummary(BaseModel):
    """Compact facility view embedded in hall responses."""
    id: int
    name: str


class HallFacilityRead(BaseModel):
    """Read model for a hall-facility association."""
    facility: FacilitySummary
    is_active: bool


class HallFacilityCreate(BaseModel):
    """Payload for attaching a facility to a hall."""
    facility_name: str


class HallFacilityUpdate(BaseModel):
    """Payload for toggling a hall-facility association."""
    hall_name: str
    facility_name: str
    is_active: bool


class HallRead(BaseModel):
    """Hall response returned by hall endpoints."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    capacity: int
    floor: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    facilities: list[HallFacilityRead] = Field(default_factory=list)