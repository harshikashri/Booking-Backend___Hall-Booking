"""Business logic for computing the free slots of a single hall."""

from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import HallNotFoundError
from src.core.exceptions import InvalidTimeWindowError
from src.data.repositories.freeSlots_repo import FreeSlotsRepository


class FreeSlotsService:
	"""Normalize search bounds and delegate availability math to the repository."""
	def __init__(self, session: AsyncSession):
		self.free_slots_repository = FreeSlotsRepository(session)

	def _normalize_datetime(self, value: datetime) -> datetime:
		"""Convert aware datetimes into naive UTC values."""
		if value.tzinfo is None:
			return value

		return value.astimezone(timezone.utc).replace(tzinfo=None)

	def _validate_time_window(
		self,
		start_datetime: datetime,
		end_datetime: datetime,
	):
		"""Ensure the requested free-slot window is valid."""
		if start_datetime >= end_datetime:
			raise InvalidTimeWindowError("Start datetime must be before end datetime")

	async def get_free_slots(
		self,
		hall_id: UUID,
		start_datetime: datetime | None = None,
		end_datetime: datetime | None = None,
	):
		"""Return the free time ranges for the selected hall."""
		now = datetime.now(timezone.utc)
		search_start = self._normalize_datetime(start_datetime or now)
		search_end = self._normalize_datetime(end_datetime or (now + timedelta(days=1)))

		self._validate_time_window(search_start, search_end)

		free_slots = await self.free_slots_repository.get_free_slots_for_hall(
			hall_id=hall_id,
			search_start=search_start,
			search_end=search_end,
		)

		if not free_slots:
			raise HallNotFoundError()

		return free_slots
