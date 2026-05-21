"""Pydantic schemas for booking requests and booking responses."""


from pydantic import BaseModel
from pydantic import ConfigDict
from datetime import datetime

from uuid import UUID

class BookingCreate(BaseModel):
	"""Payload for creating a booking."""
	hall_name: str
	start_datetime: datetime
	end_datetime: datetime


class BookingTimingUpdate(BaseModel):
	"""Payload for rescheduling an existing booking."""
	start_datetime: datetime
	end_datetime: datetime


class BookingRead(BaseModel):
	"""Booking response returned by booking endpoints."""
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	user_id: UUID
	hall_id: UUID
	start_datetime: datetime
	end_datetime: datetime
	status: str
	created_at: datetime
	updated_at: datetime


class BookingViewRead(BaseModel):
	"""Booking response that includes user and hall display names."""
	model_config = ConfigDict(from_attributes=True)

	id: UUID
	user_id: UUID
	user_name: str
	hall_id: UUID
	hall_name: str
	start_datetime: datetime
	end_datetime: datetime
	status: str
	created_at: datetime
	updated_at: datetime


"""Convenience alias for a list of booking view rows."""
BookingListRead = list[BookingViewRead]
