from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.postgres.hall import Hall


class HallRepository:
	def __init__(self, session: AsyncSession):
		self.session = session

	async def create_hall(self, hall_data: dict) -> Hall:
		hall = Hall(
			name=hall_data["name"],
			capacity=hall_data["capacity"],
			floor=hall_data["floor"],
			is_active=hall_data.get("is_active", True),
		)

		self.session.add(hall)
		await self.session.flush()
		await self.session.refresh(hall)
		return hall

	async def get_hall_by_id(self, hall_id: UUID) -> Hall | None:
		result = await self.session.execute(select(Hall).where(Hall.id == hall_id))
		return result.scalar_one_or_none()

	async def get_hall_by_name(self, name: str) -> Hall | None:
		result = await self.session.execute(select(Hall).where(Hall.name == name))
		return result.scalar_one_or_none()

	async def get_available_halls(self) -> list[Hall]:
		result = await self.session.execute(
			select(Hall).where(Hall.is_active.is_(True)).order_by(Hall.name)
		)
		return list(result.scalars().all())

	async def update_hall(self, hall: Hall, hall_data: dict) -> Hall:
		for field_name, field_value in hall_data.items():
			setattr(hall, field_name, field_value)

		await self.session.flush()
		await self.session.refresh(hall)
		return hall
