from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.rest.dependencies import get_current_admin_user
from src.api.rest.dependencies import get_current_user
from src.api.rest.dependencies import get_db_session
from src.core.services.hall_service import HallService
from src.schemas.hall_schema import HallFacilityCreate
from src.schemas.hall_schema import HallFacilityUpdate
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


@router.get(
	"/all",
	response_model=list[HallRead],
	status_code=status.HTTP_200_OK,
)
async def get_all_halls(
	admin_user: dict = Depends(get_current_admin_user),
	session: AsyncSession = Depends(get_db_session),
):
	hall_service = HallService(session)
	return await hall_service.get_all_halls()


@router.patch("/", response_model=HallRead, status_code=status.HTTP_200_OK)
async def update_hall(
	hall_data: HallUpdate,
	admin_user: dict = Depends(get_current_admin_user),
	session: AsyncSession = Depends(get_db_session),
):
	hall_service = HallService(session)
	update_payload = hall_data.model_dump(exclude_unset=True)
	hall_name = update_payload.pop("hall_name")
	return await hall_service.update_hall(
		hall_name,
		update_payload,
	)


@router.post(
	"/{hall_name}/facilities",
	status_code=status.HTTP_201_CREATED,
)
async def add_facility_to_hall(
	facility_data: HallFacilityCreate,
	hall_name: str = Path(..., description="Hall name"),
	admin_user: dict = Depends(get_current_admin_user),
	session: AsyncSession = Depends(get_db_session),
):
	hall_service = HallService(session)
	return await hall_service.add_facility_to_hall(
		hall_name,
		facility_data.facility_name,
	)


@router.patch(
	"/facilities",
	status_code=status.HTTP_200_OK,
)
async def update_hall_facility_status(
	facility_data: HallFacilityUpdate,
	admin_user: dict = Depends(get_current_admin_user),
	session: AsyncSession = Depends(get_db_session),
):
	hall_service = HallService(session)
	return await hall_service.update_hall_facility_status(
		facility_data.hall_name,
		facility_data.facility_name,
		facility_data.is_active,
	)
