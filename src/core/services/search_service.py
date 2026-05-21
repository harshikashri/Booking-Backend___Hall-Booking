"""Business logic for hall availability search queries."""

from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import InvalidTimeWindowError
from src.data.repositories.search_repo import SearchRepository


class SearchService:
	"""Validate search input and shape search results for API responses."""
	def __init__(self, session: AsyncSession):
		self.search_repository = SearchRepository(session)

	def _validate_datetime_range(
		self,
		start_datetime: datetime,
		end_datetime: datetime,
	):
		"""Validate that the search window has a positive duration."""
		if start_datetime >= end_datetime:
			raise InvalidTimeWindowError("Start datetime must be before end datetime")

	async def search_available_halls(
		self,
		search_start: datetime,
		search_end: datetime,
		hall_id: UUID | None = None,
		hall_name: str | None = None,
		facility_id: int | None = None,
		facility_name: str | None = None,
	) -> dict:
		"""Return halls and the time slots available within the search window."""
		# Validate datetime range before touching the database.
		self._validate_datetime_range(search_start, search_end)

		# The search can run with only a date window so users can browse all halls.

		results = await self.search_repository.search_halls(
			search_start=search_start,
			search_end=search_end,
			hall_id=hall_id,
			hall_name=hall_name,
			facility_id=facility_id,
			facility_name=facility_name,
		)

		return {
			"search_filters": {
				"start_datetime": search_start,
				"end_datetime": search_end,
				"hall_id": hall_id,
				"hall_name": hall_name,
				"facility_id": facility_id,
				"facility_name": facility_name,
			},
			"results": results,
		}
