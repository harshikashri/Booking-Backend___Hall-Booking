"""Persistence helpers for user favorites."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models.postgres.favorite import Favorite
from src.data.models.postgres.hall import Hall


class FavoriteRepository:
	"""Handle favorite-row lookups and persistence."""
	def __init__(self, session: AsyncSession):
		self.session = session

	async def get_hall_by_name(self, hall_name: str) -> Hall | None:
		"""Resolve a hall by name for favorite operations."""
		result = await self.session.execute(select(Hall).where(Hall.name == hall_name))
		return result.scalar_one_or_none()

	async def get_favorite_by_user_and_hall(
		self,
		user_id: UUID,
		hall_id: UUID,
	) -> Favorite | None:
		"""Return the favorite row for a user/hall pair, if present."""
		result = await self.session.execute(
			select(Favorite)
			.where(Favorite.user_id == user_id, Favorite.hall_id == hall_id)
		)
		return result.scalar_one_or_none()

	async def add_favorite(self, user_id: UUID, hall_id: UUID) -> Favorite:
		"""Create a favorite row for the supplied user/hall pair."""
		favorite = Favorite(user_id=user_id, hall_id=hall_id)
		self.session.add(favorite)
		await self.session.flush()
		await self.session.refresh(favorite)
		return favorite

	async def delete_favorite(self, user_id: UUID, hall_id: UUID) -> Favorite | None:
		"""Delete the favorite row for the supplied user/hall pair."""
		favorite = await self.get_favorite_by_user_and_hall(user_id, hall_id)
		if not favorite:
			return None

		await self.session.delete(favorite)
		await self.session.flush()
		return favorite
