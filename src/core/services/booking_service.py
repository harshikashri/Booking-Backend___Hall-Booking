"""Business logic for booking creation, cancellation, and timing updates."""

from __future__ import annotations

from datetime import datetime
from datetime import timezone
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AdminAccessRequiredError
from src.core.exceptions import BookingCancellationOwnershipError
from src.core.exceptions import BookingNotFoundError
from src.core.exceptions import BookingOwnershipError
from src.core.exceptions import BookingOverlapError
from src.core.exceptions import CancelledBookingUpdateError
from src.core.exceptions import HallInactiveError
from src.core.exceptions import HallNotFoundError
from src.core.exceptions import InvalidTimeWindowError
from src.core.exceptions import InvalidTokenPayloadError
from src.core.exceptions import InvalidUserIdFormatError
from src.data.repositories.booking_repo import BookingRepository


class BookingService:
    """Coordinate booking requests with repository queries and validation."""

    def __init__(self, session: AsyncSession):
        self.booking_repository = BookingRepository(session)



    def _ensure_admin_only(self, current_user: dict):
        """Raise when a non-admin user reaches an admin-only path."""
        if current_user.get("role") != "admin":
            raise AdminAccessRequiredError()

  

    def _get_user_id(self, current_user: dict) -> UUID:
        """Extract the authenticated user's UUID from the token payload."""
        user_id_value = current_user.get("user_id")

        if not user_id_value:
            raise InvalidTokenPayloadError()

        try:
            return UUID(str(user_id_value))

        except ValueError:
            raise InvalidUserIdFormatError()

    async def get_my_bookings(self, current_user: dict):
        """Return bookings for the caller's account."""
        user_id = self._get_user_id(current_user)

        return await self.booking_repository.get_bookings_by_user_id(user_id)

    async def get_all_bookings(self, current_user: dict):
        """Return all bookings for administrative views."""
        return await self.booking_repository.get_all_bookings()

    async def get_bookings_by_user_id(
        self,
        current_user: dict,
        user_id: UUID,
    ):
        """Return bookings for a specific user ID."""
        return await self.booking_repository.get_bookings_by_user_id(user_id)

    async def cancel_booking(
        self,
        current_user: dict,
        booking_id: UUID,
    ):
        """Cancel a booking owned by the authenticated user."""

        user_id = self._get_user_id(current_user)

        booking = await self.booking_repository.get_booking_by_id(booking_id)

        if not booking:
            raise BookingNotFoundError()

        if booking.user_id != user_id:
            raise BookingCancellationOwnershipError()

        await self.booking_repository.update_booking_status(booking, "cancelled")

        return {"detail": "Booking cancelled successfully"}

    def _validate_time_window(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
    ):
        """Reject inverted or empty booking windows."""
        if start_datetime >= end_datetime:
            raise InvalidTimeWindowError()

    def _normalize_datetime(self, value: datetime) -> datetime:
        """Normalize timezone-aware values to naive UTC datetimes."""
        if value.tzinfo is None:
            return value

        return value.astimezone(timezone.utc).replace(tzinfo=None)

    async def _ensure_no_overlap(
        self,
        hall_id: UUID,
        start_datetime: datetime,
        end_datetime: datetime,
        exclude_booking_id: UUID | None = None,
    ):
        """Ensure the requested window does not overlap another booking."""
        overlapping_booking = (
            await self.booking_repository.get_overlapping_booking(
                hall_id=hall_id,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                exclude_booking_id=exclude_booking_id,
            )
        )

        if overlapping_booking:
            raise BookingOverlapError()

    async def book_hall(
        self,
        current_user: dict,
        booking_data: dict,
    ):
        """Create a booking after checking hall activity and overlap rules."""

        user_id = self._get_user_id(current_user)

        hall_name = booking_data["hall_name"]

        start_datetime = self._normalize_datetime(
            booking_data["start_datetime"]
        )

        end_datetime = self._normalize_datetime(
            booking_data["end_datetime"]
        )

        self._validate_time_window(
            start_datetime,
            end_datetime,
        )

        hall = await self.booking_repository.get_hall_by_name(
            hall_name
        )

        if not hall:
            raise HallNotFoundError()

        if not hall.is_active:
            raise HallInactiveError()

        await self._ensure_no_overlap(
            hall.id,
            start_datetime,
            end_datetime,
        )

        try:
            booking = await self.booking_repository.create_booking(
                user_id=user_id,
                hall_id=hall.id,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
            )

            return booking

        except IntegrityError:
            raise InvalidTimeWindowError()

    async def update_booking_timing(
        self,
        current_user: dict,
        booking_id: UUID,
        start_datetime: datetime,
        end_datetime: datetime,
    ):
        """Move an existing booking to a new time window."""

        user_id = self._get_user_id(current_user)

        start_datetime = self._normalize_datetime(
            start_datetime
        )

        end_datetime = self._normalize_datetime(
            end_datetime
        )

        self._validate_time_window(
            start_datetime,
            end_datetime,
        )

        booking = await self.booking_repository.get_booking_by_id(
            booking_id
        )

        if not booking:
            raise BookingNotFoundError()

        if booking.user_id != user_id:
            raise BookingOwnershipError()

        if booking.status == "cancelled":
            raise CancelledBookingUpdateError()

        await self._ensure_no_overlap(
            hall_id=booking.hall_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            exclude_booking_id=booking.id,
        )

        try:
            updated_booking = (
                await self.booking_repository.update_booking_timing(
                    booking=booking,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                )
            )

            return updated_booking

        except IntegrityError:
            raise InvalidTimeWindowError()