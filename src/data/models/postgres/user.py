import uuid

from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from src.data.models.postgres.base import Base


class User(Base):

	__tablename__ = "users"

	id: Mapped[uuid.UUID] = mapped_column(
		UUID(as_uuid=True),
		primary_key=True,
		default=uuid.uuid4,
		server_default=text("gen_random_uuid()")
	)

	name: Mapped[str] = mapped_column(
		String(100),
		nullable=False
	)

	password_hash: Mapped[str] = mapped_column(
		Text,
		nullable=False
	)

	role: Mapped[str] = mapped_column(
		String(20),
		nullable=False
	)

	is_active: Mapped[bool] = mapped_column(
		Boolean,
		nullable=False,
		default=True
	)

	created_at: Mapped[DateTime] = mapped_column(
		DateTime,
		server_default=func.now(),
		nullable=False
	)

	updated_at: Mapped[DateTime] = mapped_column(
		DateTime,
		server_default=func.now(),
		onupdate=func.now(),
		nullable=False
	)