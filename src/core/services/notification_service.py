"""In-memory notification hub used to fan out booking cancellation events over SSE."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime
from datetime import timezone
from typing import Any
from uuid import UUID
from uuid import uuid4


class NotificationHub:
	"""Track per-user subscriber queues and publish notifications to them."""
	def __init__(self):
		self._subscribers: dict[str, list[asyncio.Queue[dict[str, Any]]]] = defaultdict(list)
		self._lock = asyncio.Lock()

	async def subscribe(self, user_id: str) -> asyncio.Queue[dict[str, Any]]:
		"""Register a queue for one user and return it to the caller."""
		queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

		async with self._lock:
			self._subscribers[user_id].append(queue)

		return queue

	async def unsubscribe(self, user_id: str, queue: asyncio.Queue[dict[str, Any]]) -> None:
		"""Remove a queue from a user's subscription list."""
		async with self._lock:
			queues = self._subscribers.get(user_id)
			if not queues:
				return

			if queue in queues:
				queues.remove(queue)

			if not queues:
				self._subscribers.pop(user_id, None)

	async def publish(self, user_id: str, payload: dict[str, Any]) -> None:
		"""Push a notification to every active subscriber for the user."""
		async with self._lock:
			queues = list(self._subscribers.get(user_id, []))

		for queue in queues:
			await queue.put(payload)


notification_hub = NotificationHub()


def queue_booking_cancellation_notification(
	session,
	*,
	user_id: UUID,
	booking,
	user_name: str,
	hall_name: str,
) -> None:
	"""Store a notification in session state so it can be published after commit."""
	pending_notifications = session.info.setdefault("pending_notifications", [])
	pending_notifications.append(
		{
			"id": str(uuid4()),
			"user_id": str(user_id),
			"type": "booking_cancelled_due_to_hall_disabled",
			"message": f"Your booking for {hall_name} was cancelled because the hall was disabled.",
			"user_name": user_name,
			"booking": {
				"id": str(booking.id),
				"hall_id": str(booking.hall_id),
				"hall_name": hall_name,
				"start_datetime": booking.start_datetime,
				"end_datetime": booking.end_datetime,
				"status": "cancelled",
			},
			"created_at": datetime.now(timezone.utc).isoformat(),
		}
	)


async def publish_pending_notifications(session) -> None:
	"""Publish all queued notifications after a successful transaction commit."""
	pending_notifications = session.info.pop("pending_notifications", [])

	for notification in pending_notifications:
		user_id = notification.get("user_id")
		if not user_id:
			continue

		await notification_hub.publish(str(user_id), notification)