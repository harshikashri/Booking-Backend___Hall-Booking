from fastapi import HTTPException
from fastapi import status

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

from src.data.repositories.hall_repo import HallRepository


class HallService:
	def __init__(self, session: AsyncSession):
		self.hall_repository = HallRepository(session)

	async def create_hall(self, hall_data: dict):
		existing_hall = await self.hall_repository.get_hall_by_name(hall_data["name"])

		if existing_hall:
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT,
				detail="Hall name already exists",
			)

		try:
			return await self.hall_repository.create_hall(hall_data)
		except IntegrityError:
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT,
				detail="Hall name already exists",
			)

	async def get_available_halls(self):
		return await self.hall_repository.get_available_halls_with_facilities()

	async def get_all_halls(self):
		return await self.hall_repository.get_all_halls_with_facilities()

	async def update_hall(self, hall_name: str, hall_data: dict):
		hall = await self.hall_repository.get_hall_by_name(hall_name)

		if not hall:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Hall not found",
			)

		new_name = hall_data.get("name")
		if new_name and new_name != hall.name:
			existing_hall = await self.hall_repository.get_hall_by_name(new_name)
			if existing_hall:
				raise HTTPException(
					status_code=status.HTTP_409_CONFLICT,
					detail="Hall name already exists",
				)

		update_data = {
			key: value
			for key, value in hall_data.items()
			if value is not None
		}

		try:
			return await self.hall_repository.update_hall(hall, update_data)
		except IntegrityError:
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT,
				detail="Hall update failed",
			)

	async def add_facility_to_hall(self, hall_name: str, facility_name: str):
		hall = await self.hall_repository.get_hall_by_name(hall_name)
		if not hall:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Hall not found",
			)

		facility = await self.hall_repository.get_facility_by_name(facility_name)
		if not facility:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Facility not found",
			)

		hall_facility = await self.hall_repository.add_facility_to_hall(hall_name, facility_name)
		if not hall_facility:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Hall or facility not found",
			)
		return hall_facility

	async def deactivate_hall_facility(self, hall_name: str, facility_name: str):
		hall = await self.hall_repository.get_hall_by_name(hall_name)
		if not hall:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Hall not found",
			)

		facility = await self.hall_repository.get_facility_by_name(facility_name)
		if not facility:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Facility not found",
			)

		hall_facility = await self.hall_repository.deactivate_hall_facility(hall_name, facility_name)
		if not hall_facility:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Hall facility not found",
			)

		return hall_facility

	async def update_hall_facility_status(
		self,
		hall_name: str,
		facility_name: str,
		is_active: bool,
	):
		hall = await self.hall_repository.get_hall_by_name(hall_name)
		if not hall:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Hall not found",
			)

		facility = await self.hall_repository.get_facility_by_name(facility_name)
		if not facility:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Facility not found",
			)

		hall_facility = await self.hall_repository.update_hall_facility_status(
			hall_name,
			facility_name,
			is_active,
		)
		if not hall_facility:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Hall facility not found",
			)

		return hall_facility
