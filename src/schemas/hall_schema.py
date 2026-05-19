from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field
from pydantic import ConfigDict


class HallCreate(BaseModel):
    name: str
    capacity: int
    floor: int
    is_active: bool = True


class HallUpdate(BaseModel):
    hall_name: str
    name: str | None = None
    capacity: int | None = None
    floor: int | None = None
    is_active: bool | None = None


class FacilitySummary(BaseModel):
    id: int
    name: str


class HallFacilityRead(BaseModel):
    facility: FacilitySummary
    is_active: bool


class HallFacilityCreate(BaseModel):
    facility_name: str


class HallFacilityUpdate(BaseModel):
    hall_name: str
    facility_name: str
    is_active: bool


class HallRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    capacity: int
    floor: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    facilities: list[HallFacilityRead] = Field(default_factory=list)