"""Persistence helpers for halls, hall facilities, and hall lookups."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.postgres.facility import Facility
from src.data.models.postgres.hall_facility import HallFacility
from src.data.models.postgres.hall import Hall


class HallRepository:
	"""Encapsulate hall queries and hall/facility join-table updates."""
	def __init__(self, session: AsyncSession):
		self.session = session

	async def create_hall(self, hall_data: dict) -> Hall:
		"""Insert a new hall row and return the refreshed ORM object."""
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
		"""Fetch a hall by primary key."""
		result = await self.session.execute(select(Hall).where(Hall.id == hall_id))
		return result.scalar_one_or_none()

	async def get_hall_by_name(self, name: str) -> Hall | None:
		"""Fetch a hall by its unique name."""
		result = await self.session.execute(select(Hall).where(Hall.name == name))
		return result.scalar_one_or_none()

	async def get_facility_by_name(self, name: str) -> Facility | None:
		"""Fetch a facility by name."""
		result = await self.session.execute(
			select(Facility).where(Facility.name == name)
		)
		return result.scalar_one_or_none()

	async def get_available_halls(self) -> list[Hall]:
		"""Return active halls ordered by name."""
		result = await self.session.execute(
			select(Hall).where(Hall.is_active.is_(True)).order_by(Hall.name)
		)
		return list(result.scalars().all())

	async def get_available_halls_with_facilities(self) -> list[dict]:
		"""Return active halls with their active facilities embedded."""
		halls_result = await self.session.execute(
			select(Hall).where(Hall.is_active.is_(True)).order_by(Hall.name)
		)
		halls = list(halls_result.scalars().all())

		if not halls:
			return []

		hall_ids = [hall.id for hall in halls]

		facilities_result = await self.session.execute(
			select(
				HallFacility.hall_id,
				HallFacility.is_active,
				Facility.id,
				Facility.name,
			)
			.join(Facility, HallFacility.facility_id == Facility.id)
			.where(
				HallFacility.hall_id.in_(hall_ids),
				HallFacility.is_active.is_(True),
			)
			.order_by(HallFacility.hall_id, Facility.name)
		)

		hall_facilities_by_hall: dict[UUID, list[dict]] = {hall.id: [] for hall in halls}

		for hall_id, is_active, facility_id, facility_name in facilities_result.all():
			hall_facilities_by_hall[hall_id].append(
				{
					"facility": {
						"id": facility_id,
						"name": facility_name,
					},
					"is_active": is_active,
				}
			)

		return [
			{
				"id": hall.id,
				"name": hall.name,
				"capacity": hall.capacity,
				"floor": hall.floor,
				"is_active": hall.is_active,
				"created_at": hall.created_at,
				"updated_at": hall.updated_at,
				"facilities": hall_facilities_by_hall[hall.id],
			}
			for hall in halls
		]

	async def get_all_halls_with_facilities(self) -> list[dict]:
		"""Return all halls with their facilities embedded."""
		halls_result = await self.session.execute(select(Hall).order_by(Hall.name))
		halls = list(halls_result.scalars().all())

		if not halls:
			return []

		hall_ids = [hall.id for hall in halls]

		facilities_result = await self.session.execute(
			select(
				HallFacility.hall_id,
				HallFacility.is_active,
				Facility.id,
				Facility.name,
			)
			.join(Facility, HallFacility.facility_id == Facility.id)
			.where(HallFacility.hall_id.in_(hall_ids))
			.order_by(HallFacility.hall_id, Facility.name)
		)

		hall_facilities_by_hall: dict[UUID, list[dict]] = {hall.id: [] for hall in halls}

		for hall_id, is_active, facility_id, facility_name in facilities_result.all():
			hall_facilities_by_hall[hall_id].append(
				{
					"facility": {
						"id": facility_id,
						"name": facility_name,
					},
					"is_active": is_active,
				}
			)

		return [
			{
				"id": hall.id,
				"name": hall.name,
				"capacity": hall.capacity,
				"floor": hall.floor,
				"is_active": hall.is_active,
				"created_at": hall.created_at,
				"updated_at": hall.updated_at,
				"facilities": hall_facilities_by_hall[hall.id],
			}
			for hall in halls
		]

	async def update_hall(self, hall: Hall, hall_data: dict) -> Hall:
		"""Apply field updates to a hall row and refresh it."""
		for field_name, field_value in hall_data.items():
			setattr(hall, field_name, field_value)

		await self.session.flush()
		await self.session.refresh(hall)
		return hall

	async def get_facility_by_id(self, facility_id: int):
		"""Fetch a facility by primary key."""
		result = await self.session.execute(
			select(Facility).where(Facility.id == facility_id)
		)
		return result.scalar_one_or_none()

	async def get_hall_facility_by_names(
		self,
		hall_name: str,
		facility_name: str,
	) -> HallFacility | None:
		"""Fetch the join row for a hall and facility by human-readable names."""
		result = await self.session.execute(
			select(HallFacility)
			.join(Hall, HallFacility.hall_id == Hall.id)
			.join(Facility, HallFacility.facility_id == Facility.id)
			.where(
				Hall.name == hall_name,
				Facility.name == facility_name,
			)
		)
		return result.scalar_one_or_none()

	async def get_hall_facility(
		self,
		hall_id: UUID,
		facility_id: int,
	) -> HallFacility | None:
		"""Fetch the join row for a hall and facility by IDs."""
		result = await self.session.execute(
			select(HallFacility).where(
				HallFacility.hall_id == hall_id,
				HallFacility.facility_id == facility_id,
			)
		)
		return result.scalar_one_or_none()

	async def add_facility_to_hall(
		self,
		hall_name: str,
		facility_name: str,
	) -> HallFacility:
		"""Create or reactivate a hall/facility association."""
		hall = await self.get_hall_by_name(hall_name)
		facility = await self.get_facility_by_name(facility_name)

		if not hall or not facility:
			return None

		hall_facility = await self.get_hall_facility(hall.id, facility.id)

		if hall_facility:
			hall_facility.is_active = True
			await self.session.flush()
			await self.session.refresh(hall_facility)
			return hall_facility

		hall_facility = HallFacility(
			hall_id=hall.id,
			facility_id=facility.id,
			is_active=True,
		)

		self.session.add(hall_facility)
		await self.session.flush()
		await self.session.refresh(hall_facility)
		return hall_facility

	async def deactivate_hall_facility(
		self,
		hall_name: str,
		facility_name: str,
	) -> HallFacility | None:
		"""Mark a hall/facility association inactive."""
		hall_facility = await self.get_hall_facility_by_names(hall_name, facility_name)

		if not hall_facility:
			return None

		hall_facility.is_active = False
		await self.session.flush()
		await self.session.refresh(hall_facility)
		return hall_facility

	async def update_hall_facility_status(
		self,
		hall_name: str,
		facility_name: str,
		is_active: bool,
	) -> HallFacility | None:
		"""Set the active state on a hall/facility association."""
		hall_facility = await self.get_hall_facility_by_names(hall_name, facility_name)

		if not hall_facility:
			return None

		hall_facility.is_active = is_active
		await self.session.flush()
		await self.session.refresh(hall_facility)
		return hall_facility
