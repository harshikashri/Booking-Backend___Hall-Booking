"""Business logic for creating facilities."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import FacilityAlreadyExistsError
from src.data.repositories.facility_repo import FacilityRepository


class FacilityService:
	"""Validate facility creation and delegate persistence to the repository."""
	def __init__(self, session: AsyncSession):
		self.facility_repository = FacilityRepository(session)

	async def get_all_facilities(self):
		"""Return every facility available for hall assignment."""
		return await self.facility_repository.get_all_facilities()

	async def create_facility(self, facility_data: dict):
		"""Create a facility if the name does not already exist."""
		existing_facility = await self.facility_repository.get_facility_by_name(
			facility_data["name"]
		)

		if existing_facility:
			raise FacilityAlreadyExistsError()

		try:
			return await self.facility_repository.create_facility(facility_data)
		except IntegrityError:
			raise FacilityAlreadyExistsError()
