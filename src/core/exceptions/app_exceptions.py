"""Application exception hierarchy for the booking backend.

These exceptions keep business rules independent from HTTP transport details.
The middleware layer maps them back to JSON responses.
"""


class AppException(Exception):
	"""Base class for all custom application errors."""

	status_code = 500
	default_detail = "Internal server error"

	def __init__(self, detail: str | None = None):
		# Store a stable message so the middleware can serialize it later.
		self.detail = detail or self.default_detail
		super().__init__(self.detail)


class ClientError(AppException):
	"""Base class for user-facing failures that should map to 4xx responses."""

	status_code = 400


class BadRequestError(ClientError):
	"""Base class for malformed input and invalid state transitions."""

	status_code = 400


class UnauthorizedError(ClientError):
	"""Base class for authentication failures."""

	status_code = 401


class ForbiddenError(ClientError):
	"""Base class for authorization failures."""

	status_code = 403


class NotFoundError(ClientError):
	"""Base class for missing resource errors."""

	status_code = 404


class ConflictError(ClientError):
	"""Base class for resource conflict errors."""

	status_code = 409


class InvalidTokenPayloadError(UnauthorizedError):
	"""Raised when the JWT payload does not contain the expected claims."""

	default_detail = "Invalid token payload"


class InvalidUserIdFormatError(UnauthorizedError):
	"""Raised when the user ID claim cannot be converted to a UUID."""

	default_detail = "Invalid user ID format in token"


class AdminAccessRequiredError(ForbiddenError):
	"""Raised when a non-admin caller reaches an admin-only path."""

	default_detail = "Admin access required"


class UserAccessRequiredError(ForbiddenError):
	"""Raised when a non-user caller reaches a user-only path."""

	default_detail = "User access required"


class HallNotFoundError(NotFoundError):
	"""Raised when a hall lookup fails."""

	default_detail = "Hall not found"


class HallInactiveError(BadRequestError):
	"""Raised when a caller tries to book a disabled hall."""

	default_detail = "Hall is inactive"


class HallAlreadyExistsError(ConflictError):
	"""Raised when hall creation or rename collides with an existing hall."""

	default_detail = "Hall name already exists"


class HallUpdateFailedError(ConflictError):
	"""Raised when a hall update cannot be persisted."""

	default_detail = "Hall update failed"


class HallFacilityNotFoundError(NotFoundError):
	"""Raised when a hall-facility association lookup fails."""

	default_detail = "Hall facility not found"


class FacilityNotFoundError(NotFoundError):
	"""Raised when a facility lookup fails."""

	default_detail = "Facility not found"


class FacilityAlreadyExistsError(ConflictError):
	"""Raised when facility creation collides with an existing facility."""

	default_detail = "Facility name already exists"


class BookingNotFoundError(NotFoundError):
	"""Raised when a booking lookup fails."""

	default_detail = "Booking not found"


class BookingOwnershipError(ForbiddenError):
	"""Raised when a user tries to mutate another user's booking."""

	default_detail = "You can only update your own booking"


class BookingCancellationOwnershipError(ForbiddenError):
	"""Raised when a user tries to cancel another user's booking."""

	default_detail = "You can only cancel your own booking"


class InvalidTimeWindowError(BadRequestError):
	"""Raised when a search or booking time window is not valid."""

	default_detail = "Start time must be before end time"


class CancelledBookingUpdateError(BadRequestError):
	"""Raised when a cancelled booking is edited."""

	default_detail = "Cancelled booking cannot be updated"


class BookingOverlapError(ConflictError):
	"""Raised when a booking overlaps an existing booking for a hall."""

	default_detail = "Booking time overlaps with an existing booking for this hall"


class FavoriteAlreadyExistsError(ConflictError):
	"""Raised when a hall is already saved in favorites."""

	default_detail = "Hall is already in favorites"


class FavoriteNotFoundError(NotFoundError):
	"""Raised when a favorite row cannot be found."""

	default_detail = "Favorite not found"