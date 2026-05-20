from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.postgres.booking import Booking
from src.data.models.postgres.hall import Hall


class FreeSlotsRepository:
	def __init__(self, session: AsyncSession):
		self.session = session

	def _calculate_available_slots(
		self,
		search_start: datetime,
		search_end: datetime,
		bookings: list[Booking],
	) -> list[dict]:
		if not bookings:
			duration = (search_end - search_start).total_seconds() // 60
			return [
				{
					"start_time": search_start,
					"end_time": search_end,
					"duration_minutes": int(duration),
				}
			]

		sorted_bookings = sorted(bookings, key=lambda booking: booking.start_datetime)
		available_slots = []
		current_time = search_start

		for booking in sorted_bookings:
			if booking.status == "cancelled":
				continue

			if current_time < booking.start_datetime:
				duration = (booking.start_datetime - current_time).total_seconds() // 60
				available_slots.append(
					{
						"start_time": current_time,
						"end_time": booking.start_datetime,
						"duration_minutes": int(duration),
					}
				)

			if booking.end_datetime > current_time:
				current_time = booking.end_datetime

		if current_time < search_end:
			duration = (search_end - current_time).total_seconds() // 60
			available_slots.append(
				{
					"start_time": current_time,
					"end_time": search_end,
					"duration_minutes": int(duration),
				}
			)

		return available_slots

	async def get_hall_by_id(self, hall_id: UUID) -> Hall | None:
		result = await self.session.execute(select(Hall).where(Hall.id == hall_id))
		return result.scalar_one_or_none()

	async def get_bookings_for_hall_in_window(
		self,
		hall_id: UUID,
		search_start: datetime,
		search_end: datetime,
	) -> list[Booking]:
		result = await self.session.execute(
			select(Booking)
			.where(
				and_(
					Booking.hall_id == hall_id,
					Booking.start_datetime < search_end,
					Booking.end_datetime > search_start,
				),
				Booking.status != "cancelled",
			)
			.order_by(Booking.start_datetime)
		)
		return list(result.scalars().all())

	async def get_free_slots_for_hall(
		self,
		hall_id: UUID,
		search_start: datetime,
		search_end: datetime,
	) -> dict | None:
		hall = await self.get_hall_by_id(hall_id)

		if not hall:
			return None

		bookings = await self.get_bookings_for_hall_in_window(
			hall_id=hall_id,
			search_start=search_start,
			search_end=search_end,
		)

		available_slots = self._calculate_available_slots(
			search_start=search_start,
			search_end=search_end,
			bookings=bookings,
		)

		return {
			"hall_id": hall.id,
			"hall_name": hall.name,
			"capacity": hall.capacity,
			"floor": hall.floor,
			"search_start_datetime": search_start,
			"search_end_datetime": search_end,
			"available_slots": available_slots,
		}
