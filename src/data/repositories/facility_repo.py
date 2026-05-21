"""Persistence helpers for facilities."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.postgres.facility import Facility


class FacilityRepository:
	"""Encapsulate facility inserts and lookups."""
	def __init__(self, session: AsyncSession):
		self.session = session

	async def create_facility(self, facility_data: dict) -> Facility:
		"""Insert a new facility row and return the refreshed ORM object."""
		facility = Facility(
			name=facility_data["name"],
		)

		self.session.add(facility)
		await self.session.flush()
		await self.session.refresh(facility)
		return facility

	async def get_facility_by_name(self, name: str) -> Facility | None:
		"""Fetch a facility by its unique name."""
		result = await self.session.execute(
			select(Facility).where(Facility.name == name)
		)
		return result.scalar_one_or_none()
