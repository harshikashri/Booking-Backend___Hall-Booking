"""Server-sent event route for booking-related notifications."""

from __future__ import annotations

import asyncio
import json
from uuid import UUID

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Query
from fastapi import status
from fastapi.responses import StreamingResponse

from src.api.rest.dependencies import get_current_user_from_token
from src.core.services.notification_service import notification_hub


router = APIRouter(
	prefix="/notifications",
	tags=["Notifications"],
)


@router.get("/stream", status_code=status.HTTP_200_OK)
async def stream_notifications(token: str = Query(..., min_length=1)):
	"""Stream notifications to the authenticated user over SSE."""
	payload = get_current_user_from_token(token)
	if not payload.get("user_id"):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid token payload",
		)
	user_id = str(UUID(str(payload["user_id"])))
	queue = await notification_hub.subscribe(user_id)

	async def event_stream():
		try:
			yield ": connected\n\n"
			while True:
				try:
					notification = await asyncio.wait_for(queue.get(), timeout=15)
					yield "event: notification\n"
					yield f"data: {json.dumps(notification, default=str)}\n\n"
				except asyncio.TimeoutError:
					yield ": keepalive\n\n"
		finally:
			await notification_hub.unsubscribe(user_id, queue)

	return StreamingResponse(
		event_stream(),
		media_type="text/event-stream",
		headers={
			"Cache-Control": "no-cache",
			"Connection": "keep-alive",
			"X-Accel-Buffering": "no",
		},
	)