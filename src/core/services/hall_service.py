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
		return await self.hall_repository.get_available_halls()

	async def update_hall(self, hall_id: UUID, hall_data: dict):
		hall = await self.hall_repository.get_hall_by_id(hall_id)

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
