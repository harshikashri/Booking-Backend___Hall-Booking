from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.rest.dependencies import get_current_user
from src.api.rest.dependencies import get_db_session
from src.core.services.favorite_service import FavoriteService


router = APIRouter(
	prefix="/favorites",
	tags=["Favorites"],
)


@router.post(
	"/{hall_name}",
	status_code=status.HTTP_201_CREATED,
)
async def add_favorite(
	hall_name: str = Path(..., description="Hall name"),
	current_user: dict = Depends(get_current_user),
	session: AsyncSession = Depends(get_db_session),
):
	favorite_service = FavoriteService(session)
	return await favorite_service.add_favorite(current_user, hall_name)


@router.delete(
	"/{hall_name}",
	status_code=status.HTTP_200_OK,
)
async def delete_favorite(
	hall_name: str = Path(..., description="Hall name"),
	current_user: dict = Depends(get_current_user),
	session: AsyncSession = Depends(get_db_session),
):
	favorite_service = FavoriteService(session)
	return await favorite_service.delete_favorite(current_user, hall_name)
