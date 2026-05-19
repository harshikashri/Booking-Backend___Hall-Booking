from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi import status

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.rest.dependencies import get_current_admin_user
from src.api.rest.dependencies import get_current_user
from src.api.rest.dependencies import get_db_session
from src.core.services.hall_service import HallService
from src.schemas.hall_schema import HallCreate
from src.schemas.hall_schema import HallRead
from src.schemas.hall_schema import HallUpdate


router = APIRouter(
	prefix="/halls",
	tags=["Halls"],
)


@router.post(
	"/",
	response_model=HallRead,
	status_code=status.HTTP_201_CREATED,
)
async def create_hall(
	hall_data: HallCreate,
	admin_user: dict = Depends(get_current_admin_user),
	session: AsyncSession = Depends(get_db_session),
):
	hall_service = HallService(session)
	return await hall_service.create_hall(hall_data.model_dump())


@router.get(
	"/",
	response_model=list[HallRead],
	status_code=status.HTTP_200_OK,
)
async def get_halls(
	current_user: dict = Depends(get_current_user),
	session: AsyncSession = Depends(get_db_session),
):
	hall_service = HallService(session)
	return await hall_service.get_available_halls()


@router.patch(
	"/{hall_id}",
	response_model=HallRead,
	status_code=status.HTTP_200_OK,
)
async def update_hall(
	hall_data: HallUpdate,
	hall_id: UUID = Path(..., description="Hall UUID"),
	admin_user: dict = Depends(get_current_admin_user),
	session: AsyncSession = Depends(get_db_session),
):
	hall_service = HallService(session)
	return await hall_service.update_hall(
		hall_id,
		hall_data.model_dump(exclude_unset=True),
	)
