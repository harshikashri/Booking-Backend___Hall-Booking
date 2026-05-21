"""Pydantic schemas for facility APIs."""

from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class FacilityCreate(BaseModel):
    """Payload for creating a facility."""
    name: str


class FacilityRead(BaseModel):
    """Facility response returned by facility endpoints."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime