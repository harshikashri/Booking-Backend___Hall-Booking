"""Facility routes for admin-only facility creation."""

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.rest.dependencies import get_current_admin_user
from src.api.rest.dependencies import get_db_session
from src.core.services.facility_service import FacilityService
from src.schemas.facility_schema import FacilityCreate
from src.schemas.facility_schema import FacilityRead


router = APIRouter(
	prefix="/facilities",
	tags=["Facilities"],
)


@router.get(
	"/",
	response_model=list[FacilityRead],
)
async def get_all_facilities(
	admin_user: dict = Depends(get_current_admin_user),
	session: AsyncSession = Depends(get_db_session),
):
	"""Return all facilities available for hall assignment."""
	facility_service = FacilityService(session)
	return await facility_service.get_all_facilities()


@router.post(
	"/",
	response_model=FacilityRead,
	status_code=status.HTTP_201_CREATED,
)
async def create_facility(
	facility_data: FacilityCreate,
	admin_user: dict = Depends(get_current_admin_user),
	session: AsyncSession = Depends(get_db_session),
):
	"""Create a facility record for later hall assignment."""
	facility_service = FacilityService(session)
	return await facility_service.create_facility(facility_data.model_dump())
