"""Free-slot lookup route for hall availability queries."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi import Query
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.rest.dependencies import get_db_session
from src.core.services.freeSlots_service import FreeSlotsService
from src.schemas.freeSlots_schema import FreeSlotsRead


router = APIRouter(
	prefix="/free-slots",
	tags=["Free Slots"],
)


@router.get(
	"/{hall_id}",
	response_model=FreeSlotsRead,
	status_code=status.HTTP_200_OK,
)
async def get_free_slots_for_hall(
	hall_id: UUID = Path(..., description="Hall ID"),
	start_datetime: datetime | None = Query(
		None,
		description="Search window start datetime",
	),
	end_datetime: datetime | None = Query(
		None,
		description="Search window end datetime",
	),
	session: AsyncSession = Depends(get_db_session),
):
	"""Return the free time windows for a single hall."""
	free_slots_service = FreeSlotsService(session)
	return await free_slots_service.get_free_slots(
		hall_id=hall_id,
		start_datetime=start_datetime,
		end_datetime=end_datetime,
	)
