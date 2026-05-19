from fastapi import HTTPException
from fastapi import status

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.repositories.facility_repo import FacilityRepository


class FacilityService:
	def __init__(self, session: AsyncSession):
		self.facility_repository = FacilityRepository(session)

	async def create_facility(self, facility_data: dict):
		existing_facility = await self.facility_repository.get_facility_by_name(
			facility_data["name"]
		)

		if existing_facility:
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT,
				detail="Facility name already exists",
			)

		try:
			return await self.facility_repository.create_facility(facility_data)
		except IntegrityError:
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT,
				detail="Facility name already exists",
			)
