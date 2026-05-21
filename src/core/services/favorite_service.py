"""Business logic for user favorites."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import FavoriteAlreadyExistsError
from src.core.exceptions import FavoriteNotFoundError
from src.core.exceptions import HallNotFoundError
from src.core.exceptions import InvalidTokenPayloadError
from src.core.exceptions import UserAccessRequiredError
from src.data.repositories.favorite_repo import FavoriteRepository


class FavoriteService:
	"""Enforce user-only access and manage favorite hall records."""
	def __init__(self, session: AsyncSession):
		self.favorite_repository = FavoriteRepository(session)

	def _ensure_user_only(self, current_user: dict):
		"""Require a regular user role for favorites operations."""
		if current_user.get("role") != "user":
			raise UserAccessRequiredError()

	async def add_favorite(self, current_user: dict, hall_name: str):
		"""Add the selected hall to the caller's favorites."""
		self._ensure_user_only(current_user)

		user_id_value = current_user.get("user_id")
		if not user_id_value:
			raise InvalidTokenPayloadError()

		user_id = UUID(str(user_id_value))

		hall = await self.favorite_repository.get_hall_by_name(hall_name)
		if not hall:
			raise HallNotFoundError()

		existing_favorite = await self.favorite_repository.get_favorite_by_user_and_hall(
			user_id,
			hall.id,
		)

		if existing_favorite:
			raise FavoriteAlreadyExistsError()

		return await self.favorite_repository.add_favorite(user_id, hall.id)

	async def delete_favorite(self, current_user: dict, hall_name: str):
		"""Remove the selected hall from the caller's favorites."""
		self._ensure_user_only(current_user)

		user_id_value = current_user.get("user_id")
		if not user_id_value:
			raise InvalidTokenPayloadError()

		user_id = UUID(str(user_id_value))

		hall = await self.favorite_repository.get_hall_by_name(hall_name)
		if not hall:
			raise HallNotFoundError()

		favorite = await self.favorite_repository.delete_favorite(user_id, hall.id)

		if not favorite:
			raise FavoriteNotFoundError()

		return {"detail": "Favorite removed successfully"}
