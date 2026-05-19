from uuid import UUID

from fastapi import HTTPException
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession

from src.data.repositories.favorite_repo import FavoriteRepository


class FavoriteService:
	def __init__(self, session: AsyncSession):
		self.favorite_repository = FavoriteRepository(session)

	def _ensure_user_only(self, current_user: dict):
		if current_user.get("role") != "user":
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="User access required",
			)

	async def add_favorite(self, current_user: dict, hall_name: str):
		self._ensure_user_only(current_user)

		user_id_value = current_user.get("user_id")
		if not user_id_value:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Invalid token payload",
			)

		user_id = UUID(str(user_id_value))

		hall = await self.favorite_repository.get_hall_by_name(hall_name)
		if not hall:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Hall not found",
			)

		existing_favorite = await self.favorite_repository.get_favorite_by_user_and_hall(
			user_id,
			hall.id,
		)

		if existing_favorite:
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT,
				detail="Hall is already in favorites",
			)

		return await self.favorite_repository.add_favorite(user_id, hall.id)

	async def delete_favorite(self, current_user: dict, hall_name: str):
		self._ensure_user_only(current_user)

		user_id_value = current_user.get("user_id")
		if not user_id_value:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Invalid token payload",
			)

		user_id = UUID(str(user_id_value))

		hall = await self.favorite_repository.get_hall_by_name(hall_name)
		if not hall:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Hall not found",
			)

		favorite = await self.favorite_repository.delete_favorite(user_id, hall.id)

		if not favorite:
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Favorite not found",
			)

		return {"detail": "Favorite removed successfully"}
