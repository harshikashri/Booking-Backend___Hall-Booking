"""Pydantic schemas for free-slot availability responses."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class TimeSlot(BaseModel):
	"""One contiguous available time slot."""
	start_time: datetime
	end_time: datetime
	duration_minutes: int


class FreeSlotsRead(BaseModel):
	"""Free-slot response for a single hall."""
	model_config = ConfigDict(from_attributes=True)

	hall_id: UUID
	hall_name: str
	capacity: int
	floor: int
	search_start_datetime: datetime
	search_end_datetime: datetime
	available_slots: list[TimeSlot]
