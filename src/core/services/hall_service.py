"""Business logic for hall creation, updates, and facility assignment."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

from src.core.exceptions import FacilityNotFoundError
from src.core.exceptions import HallAlreadyExistsError
from src.core.exceptions import HallFacilityNotFoundError
from src.core.exceptions import HallNotFoundError
from src.core.exceptions import HallUpdateFailedError
from src.core.services.notification_service import queue_booking_cancellation_notification
from src.data.repositories.booking_repo import BookingRepository
from src.data.repositories.hall_repo import HallRepository


class HallService:
	"""Coordinate hall updates and related facility/booking lookups."""
	def __init__(self, session: AsyncSession):
		self.hall_repository = HallRepository(session)
		self.booking_repository = BookingRepository(session)

	async def create_hall(self, hall_data: dict):
		"""Create a hall after enforcing name uniqueness."""
		existing_hall = await self.hall_repository.get_hall_by_name(hall_data["name"])

		if existing_hall:
			raise HallAlreadyExistsError()

		try:
			return await self.hall_repository.create_hall(hall_data)
		except IntegrityError:
			raise HallAlreadyExistsError()

	async def get_available_halls(self):
		"""Return only active halls for regular users."""
		return await self.hall_repository.get_available_halls_with_facilities()

	async def get_all_halls(self):
		"""Return all halls for administrative views."""
		return await self.hall_repository.get_all_halls_with_facilities()

	async def update_hall(self, hall_name: str, hall_data: dict):
		"""Update a hall and cancel dependent bookings when it is disabled."""
		hall = await self.hall_repository.get_hall_by_name(hall_name)

		if not hall:
			raise HallNotFoundError()

		new_name = hall_data.get("name")
		if new_name and new_name != hall.name:
			existing_hall = await self.hall_repository.get_hall_by_name(new_name)
			if existing_hall:
				raise HallAlreadyExistsError()

		update_data = {
			key: value
			for key, value in hall_data.items()
			if value is not None
		}
		should_cancel_bookings = hall.is_active and update_data.get("is_active") is False

		try:
			updated_hall = await self.hall_repository.update_hall(hall, update_data)
			if should_cancel_bookings:
				await self._cancel_bookings_for_disabled_hall(updated_hall)
			return updated_hall
		except IntegrityError:
			raise HallUpdateFailedError()

	async def _cancel_bookings_for_disabled_hall(self, hall):
		"""Cancel active bookings tied to a hall that was just disabled."""
		booking_records = await self.booking_repository.get_booking_records_by_hall_id(hall.id)

		for booking, user_name, hall_name in booking_records:
			await self.booking_repository.update_booking_status(booking, "cancelled")
			queue_booking_cancellation_notification(
				self.booking_repository.session,
				user_id=booking.user_id,
				booking=booking,
				user_name=user_name,
				hall_name=hall_name,
			)

	async def add_facility_to_hall(self, hall_name: str, facility_name: str):
		"""Attach a facility to a hall, creating the join row if needed."""
		hall = await self.hall_repository.get_hall_by_name(hall_name)
		if not hall:
			raise HallNotFoundError()

		facility = await self.hall_repository.get_facility_by_name(facility_name)
		if not facility:
			raise FacilityNotFoundError()

		hall_facility = await self.hall_repository.add_facility_to_hall(hall_name, facility_name)
		if not hall_facility:
			raise HallFacilityNotFoundError("Hall or facility not found")
		return hall_facility

	async def deactivate_hall_facility(self, hall_name: str, facility_name: str):
		"""Mark a hall-facility relationship inactive."""
		hall = await self.hall_repository.get_hall_by_name(hall_name)
		if not hall:
			raise HallNotFoundError()

		facility = await self.hall_repository.get_facility_by_name(facility_name)
		if not facility:
			raise FacilityNotFoundError()

		hall_facility = await self.hall_repository.deactivate_hall_facility(hall_name, facility_name)
		if not hall_facility:
			raise HallFacilityNotFoundError()

		return hall_facility

	async def update_hall_facility_status(
		self,
		hall_name: str,
		facility_name: str,
		is_active: bool,
	):
		"""Toggle the active state of a hall-facility relationship."""
		hall = await self.hall_repository.get_hall_by_name(hall_name)
		if not hall:
			raise HallNotFoundError()

		facility = await self.hall_repository.get_facility_by_name(facility_name)
		if not facility:
			raise FacilityNotFoundError()

		hall_facility = await self.hall_repository.update_hall_facility_status(
			hall_name,
			facility_name,
			is_active,
		)
		if not hall_facility:
			raise HallFacilityNotFoundError()

		return hall_facility
