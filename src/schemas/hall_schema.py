from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class HallCreate(BaseModel):
    name: str
    capacity: int
    floor: int
    is_active: bool = True


class HallUpdate(BaseModel):
    name: str | None = None
    capacity: int | None = None
    floor: int | None = None
    is_active: bool | None = None


class HallRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    capacity: int
    floor: int
    is_active: bool
    created_at: datetime
    updated_at: datetime